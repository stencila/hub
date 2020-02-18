import typing

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View

from projects.permission_models import ProjectPermissionType
from projects.project_models import Snapshot
from projects.source_operations import list_snapshot_directory, path_entry_iterator
from projects.views.mixins import ProjectPermissionsMixin
from projects.views.project_views import ProjectTab


class FileBrowserView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            version: int, path: typing.Optional[str] = None) -> HttpResponse:
        path = path or ''
        project = self.get_project(request.user, account_name, project_name)
        snapshot = get_object_or_404(Snapshot, project=project, version_number=version)
        items = list_snapshot_directory(snapshot, path)

        return render(request, 'projects/snapshot_files.html', self.get_render_context({
            'page_title': 'Snapshot {} Files'.format(snapshot.tag or snapshot.version_number),
            'breadcrumbs': path_entry_iterator(path, 'Snapshot {}'.format(snapshot.version_number)),
            'project_tab': ProjectTab.FILES.value,
            'project_subtab': ProjectTab.FILES_SNAPSHOTS.value,
            'items': items,
            'snapshot': snapshot
        }))
