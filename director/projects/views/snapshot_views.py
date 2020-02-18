import os
import typing

from django.http import HttpRequest, HttpResponse, Http404, FileResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View

from projects.permission_models import ProjectPermissionType
from projects.project_models import Snapshot
from projects.source_operations import list_snapshot_directory, path_entry_iterator, snapshot_path
from projects.views.mixins import ProjectPermissionsMixin
from projects.views.project_views import ProjectTab


class SnapshotView(ProjectPermissionsMixin, View):
    def get_snapshot(self, request: HttpRequest, account_name: str, project_name: str, version: int) -> Snapshot:
        project = self.get_project(request.user, account_name, project_name)
        return get_object_or_404(Snapshot, project=project, version_number=version)

    def get_snapshot_and_path(self, request: HttpRequest, account_name: str, project_name: str, version: int,
                              path: str) -> typing.Tuple[Snapshot, str]:
        snapshot = self.get_snapshot(request, account_name, project_name, version)

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
            'breadcrumbs': path_entry_iterator(path, 'Snapshot {}'.format(snapshot.version_number)),
            'project_tab': ProjectTab.FILES.value,
            'project_subtab': ProjectTab.FILES_SNAPSHOTS.value,
            'items': items,
            'snapshot': snapshot
        }))


class DownloadView(SnapshotView):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            version: int, path: str) -> FileResponse:
        snapshot, file_path = self.get_snapshot_and_path(request, account_name, project_name, version, path)
        return FileResponse(open(file_path, 'rb'), as_attachment=True)


class ContentView(SnapshotView):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            version: int, path: str) -> FileResponse:
        snapshot, file_path = self.get_snapshot_and_path(request, account_name, project_name, version, path)

        with open(file_path, 'r') as f:
            file_content = f.read()

        return render(request, 'projects/source_open.html', {
            'file_path': path,
            'snapshot': snapshot,
            'file_content': file_content
        })
