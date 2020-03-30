import os
import typing

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, Http404, FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.html import escape
from django.views.generic.base import View

from lib.conversion_types import conversion_format_from_path, UnknownMimeTypeError, ConversionFormatId
from lib.path_operations import utf8_path_join, utf8_basename, utf8_dirname
from projects.permission_models import ProjectPermissionType
from projects.project_archiver import SnapshotArchiver
from projects.project_models import Snapshot, PublishedItem
from projects.source_operations import list_snapshot_directory, path_entry_iterator, snapshot_path, \
    generate_snapshot_publish_directory
from projects.views.mixins import ProjectPermissionsMixin, ConverterMixin, ArchivesDirMixin
from projects.views.project_views import ProjectTab
from projects.views.publication_views import published_item_render, send_media_response


class SnapshotView(ProjectPermissionsMixin, View):
    def get_snapshot(self, request: HttpRequest, account_name: str, project_name: str, version: int) -> Snapshot:
        project = self.get_project(request.user, account_name, project_name)
        return get_object_or_404(Snapshot, project=project, version_number=version)

    def get_snapshot_and_path(self, request: HttpRequest, account_name: str, project_name: str, version: int,
                              path: typing.Optional[str] = None) -> typing.Tuple[Snapshot, typing.Optional[str]]:
        snapshot = self.get_snapshot(request, account_name, project_name, version)

        if path is None:
            file_path = None
        else:
            file_path = snapshot_path(snapshot, path)
            if not os.path.exists(file_path) or os.path.isdir(file_path):
                raise Http404

        return snapshot, file_path


class FileBrowserView(SnapshotView):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            version: int, path: typing.Optional[str] = None) -> HttpResponse:
        path = path or ''
        snapshot = self.get_snapshot(request, account_name, project_name, version)
        items = list_snapshot_directory(snapshot, path)

        return render(request, 'projects/snapshot_files.html', self.get_render_context({
            'page_title': 'Snapshot {} Files'.format(snapshot.tag or snapshot.version_number),
            'breadcrumbs': path_entry_iterator(path, str(snapshot)),
            'project_tab': ProjectTab.FILES_SNAPSHOTS.value,
            'items': items,
            'snapshot': snapshot
        }))


class DownloadView(SnapshotView):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            version: int, path: str) -> FileResponse:
        snapshot, file_path = self.get_snapshot_and_path(request, account_name, project_name, version, path)

        if file_path is None:
            raise TypeError('Can\'t open a None path. But this won\'t happen unless path being passed is None.')

        return FileResponse(open(file_path, 'rb'), as_attachment=True)


class ContentView(SnapshotView):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            version: int, path: str) -> FileResponse:
        snapshot, file_path = self.get_snapshot_and_path(request, account_name, project_name, version, path)

        if file_path is None:
            raise TypeError('Can\'t open a None path. But this won\'t happen unless path being passed is None.')

        with open(file_path, 'r') as f:
            file_content = f.read()

        return render(request, 'projects/source_open.html', {
            'file_path': path,
            'snapshot': snapshot,
            'file_content': file_content
        })


class PreviewView(ConverterMixin, SnapshotView):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            version: int, path: str) -> HttpResponse:
        snapshot, file_path = self.get_snapshot_and_path(request, account_name, project_name, version, path)
        if file_path is None:
            raise TypeError('Can\'t work with None path. But this won\'t happen unless path being passed is None.')

        pi, created = PublishedItem.objects.get_or_create(project=self.project, snapshot=snapshot,
                                                          source_path=path)

        published_path = utf8_path_join(
            generate_snapshot_publish_directory(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, snapshot),
            '{}.html'.format(pi.pk)
        )

        if created or not pi.path:
            # don't bother checking modification time since snapshots shouldn't change
            try:
                source_type = conversion_format_from_path(file_path)
                self.do_conversion(snapshot.project, request.user, source_type, file_path, ConversionFormatId.html,
                                   published_path, False)
                pi.path = published_path
                pi.save()
            except Exception as e:
                if created:
                    pi.delete()

                if not isinstance(e, (UnknownMimeTypeError, RuntimeError)):
                    raise

                filename = escape(utf8_basename(path))

                if isinstance(e, UnknownMimeTypeError):
                    error_format = 'Unable to preview <em>{}</em> as its file type could not be determined.'
                else:
                    error_format = 'Unable to preview <em>{}</em> as it could not be converted to HTML. Please ' \
                                   'check the Project Activity page for more information.'

                messages.error(request, error_format.format(filename), extra_tags='safe')

                dirname = utf8_dirname(path)
                redirect_args = [snapshot.project.account.name, snapshot.project.name, snapshot.version_number]

                if dirname:
                    redirect_args.append(dirname)
                    redirect_view = 'snapshot_files_path'
                else:
                    redirect_view = 'snapshot_files'
                return redirect(redirect_view, *redirect_args)

        project = self.project
        return published_item_render(request, pi,
                                     reverse('snapshot_files_download', args=(project.account.name, project.name,
                                                                              snapshot.version_number, pi.source_path)),
                                     'HTML Preview of {}'.format(pi.source_path))


class PreviewMediaView(SnapshotView):
    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            version: int, pi_pk: str, media_path: str) -> FileResponse:
        snapshot, _ = self.get_snapshot_and_path(request, account_name, project_name, version)

        pi = get_object_or_404(PublishedItem, project=self.project, snapshot=snapshot, pk=pi_pk)
        return send_media_response(pi, media_path)


class ArchiveView(ArchivesDirMixin, SnapshotView):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,
            version: int) -> FileResponse:  # type: ignore
        snapshot = self.get_snapshot(request, account_name, project_name, version)
        archiver = SnapshotArchiver(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, snapshot, request.user)
        archive_path = archiver.archive_snapshot()

        return FileResponse(open(archive_path, 'rb'), as_attachment=True)
