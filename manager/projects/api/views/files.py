from typing import Optional

from rest_framework import exceptions, viewsets

from manager.api.helpers import HtmxListMixin, HtmxMixin
from projects.api.serializers import FileSerializer
from projects.api.views.projects import get_project
from projects.models.files import File
from projects.models.projects import Project


class ProjectsFilesViewSet(
    HtmxMixin, HtmxListMixin, viewsets.GenericViewSet,
):
    """A view set for project files."""

    lookup_url_kwarg = "file"
    object_name = "file"
    queryset_name = "files"

    def get_project(self) -> Project:
        """
        Get the project for the current action and check user has roles.

        Requires that user has read access to the project.
        """
        return get_project(self.kwargs, self.request.user)

    def get_prefix(self) -> Optional[str]:
        """
        Get the prefix (if any) in the request.
        """
        prefix = self.request.GET.get("prefix")
        if prefix:
            if not prefix.endswith("/"):
                prefix += "/"
            return prefix
        return None

    def get_queryset(self, project: Optional[Project] = None):
        """
        Get project files.

        Allows for filtering:
          - using a search string
          - using beginning of path (e.g for subdirectory listing)
        """
        project = project or self.get_project()
        queryset = (
            File.objects.filter(project=project)
            .order_by("path")
            .select_related("project", "project__account", "job", "source")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(path__icontains=search)

        prefix = self.get_prefix()
        if prefix:
            queryset = queryset.filter(path__startswith=prefix)

        return queryset

    def get_object(self, project: Optional[Project] = None):
        """
        Get a project file.
        """
        try:
            return self.get_queryset(project).filter(id=self.kwargs["file"])[0]
        except IndexError:
            raise exceptions.NotFound

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.
        """
        return FileSerializer

    def get_response_context(self, *args, **kwargs):
        """
        Add prefix to the template rendering context.
        """
        context = super().get_response_context(*args, **kwargs)
        context["prefix"] = self.get_prefix()
        return context
