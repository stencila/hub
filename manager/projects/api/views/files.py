from typing import Optional

from rest_framework import exceptions, viewsets

from manager.api.helpers import (
    HtmxCreateMixin,
    HtmxDestroyMixin,
    HtmxListMixin,
    HtmxMixin,
    HtmxRetrieveMixin,
)
from projects.api.serializers import FileSerializer
from projects.api.views.projects import get_project
from projects.models.files import File
from projects.models.projects import Project, ProjectRole


class ProjectsFilesViewSet(
    HtmxMixin,
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxRetrieveMixin,
    HtmxDestroyMixin,
    viewsets.GenericViewSet,
):
    """A view set for project files."""

    lookup_url_kwarg = "file"
    object_name = "file"
    queryset_name = "files"

    def get_project(self) -> Project:
        """
        Get the project for the current action and check user has roles.

        Mutating actions require that the user be an AUTHOR or above.
        """
        return get_project(
            self.kwargs,
            self.request.user,
            [
                ProjectRole.AUTHOR,
                ProjectRole.EDITOR,
                ProjectRole.MANAGER,
                ProjectRole.OWNER,
            ]
            if self.action in ["create", "partial_update", "destroy"]
            else [],
        )

    def get_queryset(self, project: Optional[Project] = None):
        """Get project files."""
        project = project or self.get_project()
        queryset = (
            File.objects.filter(project=project)
            .order_by("path")
            .select_related("project", "project__account", "job", "source")
        )
        return queryset

    def get_object(self, project: Optional[Project] = None):
        """Get a project file."""
        try:
            return self.get_queryset(project).filter(id=self.kwargs["file"])[0]
        except IndexError:
            raise exceptions.NotFound

    def get_serializer_class(self):
        """Get the serializer class for the current action."""
        return FileSerializer
