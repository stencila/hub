import json

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.html import escape
from django.utils.text import slugify
from django.views.generic.base import View
from googleapiclient.errors import HttpError
from rest_framework.views import APIView

from lib.conversion_types import ConversionFormatId
from lib.google_docs_facade import extract_google_document_id_from_url, google_document_id_is_valid, GoogleDocsFacade
from lib.social_auth_token import user_social_token
from projects.disk_file_facade import DiskFileFacade, ItemType
from projects.permission_models import ProjectPermissionType
from projects.project_forms import PublishedItemForm
from projects.project_models import PublishedItem
from projects.project_views import ProjectPermissionsMixin
from projects.shared import PUBLISHED_FILE_NAME
from projects.source_content_facade import make_source_content_facade
from projects.source_models import GoogleDocsSource
from projects.source_operations import utf8_path_join
from projects.source_views import ConverterMixin


class LinkException(Exception):
    pass


class ItemPublishView(ProjectPermissionsMixin, ConverterMixin, APIView):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int):  # type: ignore
        """Create or update the `PublishedItem` for this Project."""
        project = self.get_project(request.user, pk)

        try:
            pi = PublishedItem.objects.get(project=project)
        except PublishedItem.DoesNotExist:
            pi = PublishedItem(project=project)

        data = request.data

        form = PublishedItemForm(data, initial={'project': project})

        if form.is_valid():
            original_path = form.cleaned_data['path']

            source = self.get_source(request.user, pk, form.cleaned_data.get('source_id'))
            scf = make_source_content_facade(request.user, original_path, source, project)

            published_path = scf.disk_file_facade.full_file_path(PUBLISHED_FILE_NAME)

            self.source_convert(request, project, scf, published_path, PUBLISHED_FILE_NAME, ConversionFormatId.html)

            pi.path = data['path']
            pi.slug = slugify(data['slug'])
            pi.save()

            messages.success(request, 'The file <em>{}</em> was published successfully.'.format(escape(original_path)),
                             extra_tags='safe')

            return JsonResponse({
                'success': True,
                'url': reverse('project_published_view', args=(project.pk, pi.slug))
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            })


# Views below are not DRF views, they should be

class DiskItemCreateView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk)

        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        body = json.loads(request.body)

        item_type = ItemType(body['type'])
        path = body['path']

        error = None

        if dff.item_exists(path):
            error = 'Item exists at "{}".'.format(path)
        elif item_type == ItemType.FILE:
            dff.create_file(path)
        elif item_type == ItemType.FOLDER:
            dff.create_directory(path)
        else:
            raise TypeError('Don\'t know how to create a {}'.format(item_type))

        return JsonResponse(
            {
                'success': not error,
                'error': error
            }
        )


class DiskItemMoveView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk)

        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        body = json.loads(request.body)

        source = body['source']
        destination = body['destination']

        error = None

        if not dff.item_exists(source):
            error = 'Source item does not exist at "{}".'.format(source)
        elif dff.item_exists(destination):
            error = 'Destination already exists at "{}".'.format(destination)
        else:
            dff.move_file(source, destination)

        return JsonResponse({
            'success': not error,
            'error': error
        })


class DiskItemRemoveView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk)

        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        body = json.loads(request.body)

        path = body['path']

        error = None

        if not dff.item_exists(path):
            error = 'Item does not exist at "{}".'.format(path)
        else:
            dff.remove_item(path)

        return JsonResponse({
            'success': not error,
            'error': error
        })


class SourceLinkView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        self.get_project(request.user, pk)

        body = json.loads(request.body)

        source_type = body['source_type']

        error = None

        if source_type == 'gdoc':
            try:
                self.link_google_doc(request.user, body)
            except LinkException as e:
                error = str(e)
        else:
            error = 'Unknown source type {}'.format(source_type)

        return JsonResponse({
            'success': not error,
            'error': error
        })

    def link_google_doc(self, user: User, request_body: dict) -> None:
        token = user_social_token(user, 'google')

        if token is None:
            raise LinkException('Can\'t link as no Google account is connected to Stencila Hub.')

        doc_id = request_body['document_id']

        if not doc_id:
            raise LinkException('A document ID or URL was not provided.')

        try:
            doc_id = extract_google_document_id_from_url(doc_id)
        except ValueError:
            pass  # not a URL, could just a be the ID

        if not google_document_id_is_valid(doc_id):
            raise LinkException('"{}" is not a valid Google Document ID.'.format(doc_id))

        google_app = SocialApp.objects.filter(provider='google').first()

        gdf = GoogleDocsFacade(google_app.client_id, google_app.secret, token)

        directory = request_body['directory']
        try:
            document = gdf.get_document(doc_id)
        except HttpError:
            raise LinkException('Could not retrieve the document, please check the ID/URL.')

        source = GoogleDocsSource(doc_id=doc_id)

        source.project = self.project
        source.path = utf8_path_join(directory, document['title'])
        source.save()
