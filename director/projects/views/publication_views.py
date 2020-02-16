import typing

from django.contrib import messages
from django.http import HttpRequest, FileResponse, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.html import escape
from django.views import View

from lib.conversion_types import UnknownMimeTypeError
from projects.permission_models import ProjectPermissionType
from projects.project_models import PublishedItem
from projects.source_content_facade import make_source_content_facade, NonFileError
from projects.source_models import Source
from projects.source_operations import relative_path_join, utf8_dirname, utf8_basename
from projects.views.mixins import ConverterMixin, ProjectPermissionsMixin
from projects.views.shared import get_source


class PublishedListView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str) -> HttpRequest:  # type: ignore
        project = self.get_project(request.user, account_name, project_name)

        context = {
            'project_tab': 'published',
            'published_items': PublishedItem.objects.filter(project=project, url_path__isnull=False).exclude(
                url_path='').order_by('url_path')
        }
        return render(request, 'projects/published_list.html', self.get_render_context(context))


class PublishedContentView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            path: str) -> FileResponse:
        project = self.get_project(request.user, account_name, project_name)
        pi = get_object_or_404(PublishedItem, project=project, url_path=path)

        return self.published_item_render(request, pi)

    @staticmethod
    def published_item_render(request: HttpRequest, published_item: PublishedItem,
                              title: typing.Optional[str] = None) -> HttpResponse:
        context = {
            'theme_name': 'eLife',
            'project': published_item.project,
            'source_path': published_item.source_path,
            'title': title
        }
        with open(published_item.path, 'r', encoding='utf8') as f:
            context['content'] = f.read()
        resp = render(request, 'projects/published_container.html', context)

        if 'elife' in request.GET:
            resp['Content-Security-Policy'] = 'frame-ancestors https://elifesciences.org https://*.elifesciences.org;'
            resp['X-Frame-Options'] = 'allow-from https://elifesciences.org'
            resp['X-Frame-Options'] = 'allow-from https://*.elifesciences.org'

        return resp


class PublishedMediaView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str, path: str,  # type: ignore
            media_path: str) -> FileResponse:
        project = self.get_project(request.user, account_name, project_name)
        pi = get_object_or_404(PublishedItem, project=project, url_path=path)

        # rebuild the media path
        media_path = '{}.html.media/{}'.format(pi.pk, media_path)

        full_path = relative_path_join(utf8_dirname(pi.path), media_path)

        try:
            fp = open(full_path, 'rb')
        except FileNotFoundError:
            raise Http404

        return FileResponse(fp)  # FileResponse closes the pointer when finished


class PreviewMediaView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str, pi_pk: str,  # type: ignore
            media_path: str) -> FileResponse:
        project = self.get_project(request.user, account_name, project_name)
        pi = get_object_or_404(PublishedItem, project=project, pk=pi_pk)

        # rebuild the media path
        media_path = '{}.html.media/{}'.format(pi.pk, media_path)

        full_path = relative_path_join(utf8_dirname(pi.path), media_path)

        try:
            fp = open(full_path, 'rb')
        except FileNotFoundError:
            raise Http404

        return FileResponse(fp)  # FileResponse closes the pointer when finished


class SourcePreviewView(ConverterMixin, PublishedContentView):
    """
    Convert a source file to HTML and return the generated HTML.

    Will attempt to load an existing PublishedItem for the source, if one exists. It will also compare the file/sources
    modification time with that of the PublishedItem and regenerate the HTML if the source data has changed.
    """

    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            path: str) -> HttpResponse:
        project = self.get_project(request.user, account_name, project_name)
        source = get_source(request.user, project, path)

        scf = make_source_content_facade(request.user, path, source, project)

        pi, created = PublishedItem.objects.get_or_create(project=project, source_path=path,
                                                          source=source if isinstance(source, Source) else None)

        if created or scf.source_modification_time > pi.updated or not pi.path:
            try:
                self.convert_and_publish(request.user, project, pi, created, source, path)
            except (NonFileError, UnknownMimeTypeError) as e:
                if isinstance(e, UnknownMimeTypeError):
                    messages.error(request,
                                   'Unable to preview <em>{}</em> as its file type could not be determined.'.format(
                                       escape(utf8_basename(path))), extra_tags='safe')

                # User might have just entered a bad URL to try to preview, just go back to file view
                return redirect('project_files', account_name, project_name)

        return self.published_item_render(request, pi, 'HTML Preview of {}'.format(pi.source_path))
