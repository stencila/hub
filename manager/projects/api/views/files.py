from typing import Any, Dict, List, Optional, Union

from django.db.models import QuerySet, TextField, Value
from django.db.models.functions import Concat, StrIndex, Substr
from django.http import Http404
from rest_framework import permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from manager.api.helpers import HtmxDestroyMixin, HtmxListMixin, HtmxRetrieveMixin
from projects.api.serializers import FileListSerializer, FileSerializer
from projects.api.views.projects import get_project
from projects.models.files import File
from projects.models.projects import Project
from projects.models.sources import Source


class ProjectsFilesViewSet(
    HtmxListMixin, HtmxRetrieveMixin, HtmxDestroyMixin, viewsets.GenericViewSet,
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
            File.objects.filter(project=project, current=True)
            .order_by("path")
            .select_related("project", "project__account", "job", "source")
            .prefetch_related("upstreams")
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

        # Return items sorted by path again
        return [value for key, value in sorted(groups.items(), reverse=True)]

    def get_object(self, project: Optional[Project] = None) -> File:
        """
        Get a current file.
        """
        project = project or self.get_project()

        id_or_path = self.kwargs["file"]
        try:
            identifier = dict(id=int(id_or_path))
        except ValueError:
            identifier = dict(path=id_or_path)

        try:
            return File.objects.get(project=project, current=True, **identifier)
        except File.DoesNotExist:
            raise Http404

    def get_pipeline(
        self, file: Optional[File] = None, upstream_limit: int = 5, downstream_limit=5
    ) -> QuerySet:
        """
        Get a file's pipeline.

        Returns a queryset of file entries that match the path within the project.
        The file does not need to be current.

        Currently, this only considers the first upstream and downstream. It does
        not collect branching upstreams or downstreams (e.g. more than one downstream)
        """
        file = file or self.get_object()

        here = file
        upstreams: List[Union[File, Source]] = []
        while len(upstreams) < upstream_limit:
            if here.source:
                upstreams.append(here.source)
                break
            else:
                ups = here.upstreams.all()
                if len(ups):
                    here = ups[0]
                    upstreams.append(here)
                else:
                    break

        here = file
        downstreams: List[File] = []
        while len(downstreams) < downstream_limit:
            downs = here.downstreams.all()
            if len(downs):
                here = downs[0]
                downstreams.append(here)
            else:
                break

        return upstreams, downstreams

    def get_history(self, project: Optional[Project] = None) -> QuerySet:
        """
        Get a file's history.

        Returns a queryset of file entries that match the path within the project.
        The file does not need to be current.
        """
        project = project or self.get_project()
        return (
            File.objects.filter(project=project, path=self.kwargs["file"])
            .order_by("-created")
            .select_related(
                "job", "job__creator", "job__creator__personal_account", "source",
            )
            .prefetch_related("upstreams")
        )

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.
        """
        if self.action == "list":
            return FileListSerializer
        if self.action == "destroy":
            return None
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

    # Additional API actions. These do not use the `@action` decorator
    # because they are declared as routes on the `ProjectsFilesRouter`
    # directly

    def history(self, request: Request, *args, **kwargs) -> Response:
        """
        Get the a file's history.

        Returns a paginated history of the file
        """
        queryset = self.get_history()
        pages = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    def convert(self, request: Request, *args, **kwargs) -> Response:
        """
        Convert a file to another format.

        Confirms that the destination path and other options are
        correct, creates a job and redirects to it.
        """
        project = self.get_project()
        file = self.get_object(project)

        path = self.request.data.get("path")

        job = file.convert(request.user, path)
        job.dispatch()

        return Response(dict(project=project, file=file, job=job))
