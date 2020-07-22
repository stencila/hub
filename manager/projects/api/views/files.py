from typing import Any, Dict, Optional

from django.db.models import TextField, Value
from django.db.models.functions import Concat, StrIndex, Substr
from rest_framework import exceptions, permissions, viewsets

from manager.api.helpers import HtmxListMixin
from projects.api.serializers import FileSerializer
from projects.api.views.projects import get_project
from projects.models.files import File
from projects.models.projects import Project


class ProjectsFilesViewSet(
    HtmxListMixin, viewsets.GenericViewSet,
):
    """A view set for project files."""

    lookup_url_kwarg = "file"
    object_name = "file"
    queryset_name = "files"

    def get_permissions(self):
        """
        Get the permissions that the current action requires.

        Actions `list` and `retreive` do not require authentication
        for public projects (i.e. anon users can view sources).
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_project(self) -> Project:
        """
        Get the project for the current action and check user has roles.

        Requires that user has read access to the project.
        """
        if not hasattr(self, "project"):
            self.project = get_project(self.kwargs, self.request.user)
        return self.project

    def get_prefix(self) -> str:
        """
        Get the prefix for the current request.

        Ensures that it has a trailing slash.
        """
        prefix = self.request.GET.get("prefix", "").strip()
        if prefix and not prefix.endswith("/"):
            prefix += "/"
        return prefix

    def get_queryset(self, project: Optional[Project] = None):
        """
        Get project files.

        Allows for filtering:
          - using a search string
          - using path prefix (e.g for subdirectory listing)

        Allows for aggregation (the default) by directory.
        """
        project = project or self.get_project()

        queryset = (
            File.objects.filter(project=project)
            .order_by("path")
            .select_related("project", "project__account", "job", "source")
        )

        source = self.request.GET.get("source")
        if source:
            queryset = queryset.filter(source=source)

        snapshot = self.request.GET.get("snapshot")
        if snapshot:
            queryset = queryset.filter(snapshot=snapshot)
        else:
            queryset = queryset.filter(snapshot__isnull=True)

        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(path__icontains=search)

        prefix = self.get_prefix()
        if prefix:
            queryset = queryset.filter(path__startswith=prefix)

        queryset = queryset.annotate(
            name=Substr(
                "path",
                pos=len(prefix) + 1,
                length=StrIndex(
                    # Add a trailing slash to ensure all paths
                    # will have a length
                    Concat(Substr("path", len(prefix) + 1), Value("/")),
                    Value("/"),
                )
                - 1,
                output_field=TextField(),
            )
        )

        expand = self.request.GET.get("expand")
        if expand is not None:
            return queryset

        groups: Dict[str, Dict[str, Any]] = {}
        for file in queryset.all():
            if "/" in file.path[len(prefix) + 1 :]:
                name = file.name
                info = groups.get(name)
                if not info:
                    groups[name] = dict(
                        project=file.project,
                        path=prefix + name,
                        name=file.name,
                        is_directory=True,
                        count=1,
                        source=[file.source],
                        size=file.size,
                        modified=file.modified,
                    )
                else:
                    info["count"] += 1
                    info["size"] += file.size
                    info["source"] += [file.source]
                    info["modified"] = (
                        file.modified
                        if file.modified > info["modified"]
                        else info["modified"]
                    )
            else:
                file.is_directory = False
                groups[file.path] = file
        return list(groups.values())

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
        Add breadcrumbs to template rendering context.
        """
        context = super().get_response_context(*args, **kwargs)

        context["project"] = self.get_project()

        breadcrumbs = [("root", "")]
        path = ""
        for name in self.get_prefix().split("/"):
            if name:
                path += name + "/"
                breadcrumbs.append((name, path))
        context["breadcrumbs"] = breadcrumbs

        return context
