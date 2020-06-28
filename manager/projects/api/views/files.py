from typing import Optional

from django.db.models import TextField, Value
from django.db.models.functions import Concat, StrIndex, Substr
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

    def get_queryset(self, project: Optional[Project] = None, aggregate: bool = False):
        """
        Get project files.

        Allows for filtering:
          - using a search string
          - using path prefix (e.g for subdirectory listing)
        """
        project = project or self.get_project()
        queryset = (
            File.objects.filter(project=project)
            .order_by("path")
            .select_related("project", "project__account", "job", "source")
        )

        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(path__icontains=search)

        prefix = self.request.GET.get("prefix", "").strip()
        if prefix:
            if not prefix.endswith("/"):
                prefix += "/"
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

        aggregate = aggregate or self.request.GET.get("aggregate")
        if aggregate is not None:
            groups = {}
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
