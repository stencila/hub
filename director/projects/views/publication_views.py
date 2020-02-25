import typing

from django.contrib import messages
from django.http import HttpRequest, FileResponse, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.html import escape
from django.views import View

from lib.conversion_types import UnknownMimeTypeError
from lib.path_operations import utf8_basename, utf8_dirname
from projects.permission_models import ProjectPermissionType
from projects.project_models import PublishedItem
from projects.source_content_facade import make_source_content_facade, NonFileError
from projects.source_models import Source
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


def published_item_render(request: HttpRequest, published_item: PublishedItem, download_url: str,
                          title: typing.Optional[str] = None) -> HttpResponse:
    context = {
        'theme_name': 'eLife',
        'title': title,
        'download_url': download_url
    }
    with open(published_item.path, 'r', encoding='utf8') as f:
        context['content'] = f.read()
    resp = render(request, 'projects/published_container.html', context)

    if 'elife' in request.GET:
        resp['Content-Security-Policy'] = 'frame-ancestors https://elifesciences.org https://*.elifesciences.org;'
        resp['X-Frame-Options'] = 'allow-from https://elifesciences.org'
        resp['X-Frame-Options'] = 'allow-from https://*.elifesciences.org'

    return resp


def send_media_response(pi: PublishedItem, media_path: str) -> FileResponse:
    # rebuild the media path
    full_path = pi.media_path(media_path)

    try:
        fp = open(full_path, 'rb')
    except FileNotFoundError:
        raise Http404

    return FileResponse(fp)  # FileResponse closes the pointer when finished


class PublishedContentView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            path: str) -> HttpResponse:
        project = self.get_project(request.user, account_name, project_name)
        pi = get_object_or_404(PublishedItem, project=project, url_path=path)

        return published_item_render(request, pi,
                                     reverse('file_source_download', args=(project.account.name, project.name,
                                                                           pi.source_path)))


class PublishedMediaView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str, path: str,  # type: ignore
            media_path: str) -> FileResponse:
        project = self.get_project(request.user, account_name, project_name)
        pi = get_object_or_404(PublishedItem, project=project, url_path=path)

        return send_media_response(pi, media_path)


class PreviewMediaView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str, pi_pk: str,  # type: ignore
            media_path: str) -> FileResponse:
        project = self.get_project(request.user, account_name, project_name)
        pi = get_object_or_404(PublishedItem, project=project, pk=pi_pk)
        return send_media_response(pi, media_path)


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
                self.convert_and_publish(request.user, project, pi, created, source, path, scf)
            except (NonFileError, UnknownMimeTypeError, RuntimeError) as e:
                filename = utf8_basename(path)
                directory = utf8_dirname(path)

                # by default, no message since the user might have just entered a bad URL
                message_format: typing.Optional[str] = None

                if isinstance(e, RuntimeError):
                    message_format = 'Unable to preview <em>{}</em> as it could not be converted to HTML. Please ' \
                                     'check the Project Activity page for more information.'
                elif isinstance(e, UnknownMimeTypeError):
                    message_format = 'Unable to preview <em>{}</em> as its file type could not be determined.'
                    messages.error(request,
                                   'Unable to preview <em>{}</em> as its file type could not be determined.'.format(
                                       escape(utf8_basename(path))), extra_tags='safe')

                if message_format:
                    messages.error(request, message_format.format(escape(filename)), extra_tags='safe')
                if directory:
                    return redirect('project_files_path', account_name, project, directory)
                return redirect('project_files', account_name, project_name)

        return published_item_render(request, pi,
                                     reverse('file_source_download', args=(project.account.name, project.name,
                                                                           pi.source_path)),
                                     'HTML Preview of {}'.format(pi.source_path))
