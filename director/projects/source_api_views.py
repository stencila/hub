import json
import os
import shutil
import typing

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.views.generic.base import View
from googleapiclient.errors import HttpError
from rest_framework.views import APIView

from lib.conversion_types import ConversionFormatId
from lib.converter_facade import fetch_url
from lib.google_docs_facade import extract_google_document_id_from_url, google_document_id_is_valid, GoogleDocsFacade
from lib.social_auth_token import user_social_token
from projects.disk_file_facade import DiskFileFacade, ItemType
from projects.permission_facade import fetch_project_for_user
from projects.permission_models import ProjectPermissionType
from projects.project_forms import PublishedItemForm
from projects.project_models import PublishedItem, Project
from projects.project_views import ProjectPermissionsMixin
from projects.source_content_facade import make_source_content_facade
from projects.source_models import GoogleDocsSource, UrlSource, Source
from projects.source_operations import utf8_path_join, generate_project_publish_directory
from projects.source_views import ConverterMixin
from projects.url_helpers import project_url_reverse


class LinkException(Exception):
    pass


def get_project_publish_directory(project: Project) -> str:
    return generate_project_publish_directory(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)


def setup_publish_directory(project: Project) -> None:
    """Create directories and sub-directories to store HTML output for published files."""
    publish_dir = get_project_publish_directory(project)
    if not os.path.exists(publish_dir):
        os.makedirs(publish_dir, True)


class ItemPublishView(ProjectPermissionsMixin, ConverterMixin, APIView):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, **kwargs):  # type: ignore
        """Create or update the `PublishedItem` for this Project."""
        project = self.get_project(request.user, kwargs)

        data = request.data

        form = PublishedItemForm(data, initial={'project': project})

        if form.is_valid():
            try:
                pi = PublishedItem.objects.get(project=project, url_path=form.cleaned_data['url_path'])
            except PublishedItem.DoesNotExist:
                pi = PublishedItem(project=project, url_path=form.cleaned_data['url_path'])

            pi.save()  # get the PK

            original_path = form.cleaned_data['path']

            source = self.get_source(request.user, kwargs, form.cleaned_data.get('source_id'))
            scf = make_source_content_facade(request.user, original_path, source, project)

            published_path = os.path.join(get_project_publish_directory(project), '{}.html'.format(pi.pk))

            absolute_input_path = scf.sync_content()

            self.do_conversion(scf.source_type, absolute_input_path, ConversionFormatId.html, published_path,
                               False)

            pi.source_path = data['path']
            pi.path = published_path
            pi.url_path = form.cleaned_data['url_path']
            if isinstance(source, Source):
                pi.source = source
            else:
                pi.source = None
            pi.save()

            success_message = 'The file <em>{}</em> was published successfully to <a href="{}">{}</a>'.format(
                escape(original_path),
                project_url_reverse('project_published_content', [pi.url_path], project=project),
                pi.url_path
            )
            messages.success(request, success_message, extra_tags='safe')

            return JsonResponse({
                'success': True,
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            })


class PublishedItemDeleteView(ProjectPermissionsMixin, APIView):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        pi = get_object_or_404(PublishedItem, pk=pk)
        self.project_fetch_result = fetch_project_for_user(request.user, project=pi.project)
        pi_url_path = pi.url_path
        self.test_required_project_permission()
        if os.path.exists(pi.path):
            os.unlink(pi.path)

        media_dir = pi.path + '.media'
        if os.path.exists(media_dir):
            shutil.rmtree(media_dir)

        pi.delete()

        if request.is_ajax():
            return JsonResponse(
                {'success': True, 'message': 'Item at {} was successfully unpublished.'.format(pi_url_path)})

        messages.success(request, 'Item at <em>{}</em> was successfully unpublished.'.format(escape(pi_url_path)),
                         extra_tags='safe')

        return HttpResponse(status=204)


class SourceLinkView(ProjectPermissionsMixin, APIView):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        self.get_project(request.user, pk)

        data = request.data

        source_type = data['source_type']

        error = None
        errors: typing.Dict[str, str] = {}

        directory = data['directory']

        if source_type == 'gdoc':
            try:
                self.link_google_doc(request.user, data, directory)
            except LinkException as e:
                error = str(e)
        elif source_type == 'url':
            self.link_url(data, directory, errors)
        else:
            error = 'Unknown source type {}'.format(source_type)

        resp: typing.Dict[str, typing.Any] = {
            'success': not error and not errors
        }

        if errors:
            resp['errors'] = errors
        else:
            resp['error'] = error

        return JsonResponse(resp)

    def link_google_doc(self, user: User, request_body: dict, directory: str) -> None:
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

        try:
            document = gdf.get_document(doc_id)
        except HttpError:
            raise LinkException('Could not retrieve the document, please check the ID/URL.')

        title = document['title']

        source = GoogleDocsSource(
            doc_id=doc_id,
            project=self.project,
            path=utf8_path_join(directory, title.replace('/', '-'))
        )

        source.save()
        messages.success(self.request, 'Google Doc <em>{}</em> was linked.'.format(escape(title)), extra_tags='safe')

    def link_url(self, request_body: dict, directory: str, errors: dict) -> None:
        url = request_body['url']

        try:
            URLValidator()(url)
        except ValidationError:
            errors['url'] = '"{}" is not a valid URL.'.format(url)

        filename = request_body['filename']

        if filename == '':
            errors['filename'] = 'The filename must be set.'
        elif '/' in filename or ':' in filename or '\\' in filename or ';' in filename:
            errors['filename'] = 'The filename must not contain the characters /, :, \\ or ;.'

        if errors:
            return

        fetch_url(url, user_agent=settings.STENCILA_CLIENT_USER_AGENT)
        path = utf8_path_join(directory, filename.replace('/', '-'))
        source = UrlSource(url=url,
                           project=self.project,
                           path=path
                           )
        source.save()
        messages.success(self.request, 'URL <em>{}</em> was linked.'.format(escape(url)), extra_tags='safe')


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
