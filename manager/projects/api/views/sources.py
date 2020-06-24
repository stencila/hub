from django.db.models import Q
from django.http.request import HttpRequest
from django.shortcuts import redirect, reverse
from rest_framework import exceptions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from jobs.api.helpers import redirect_to_job
from manager.api.helpers import (
    HtmxCreateMixin,
    HtmxDestroyMixin,
    HtmxListMixin,
    HtmxMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
)
from projects.api.serializers import SourcePolymorphicSerializer
from projects.api.views.projects import ProjectsViewSet
from projects.models.projects import Project, ProjectRole
from projects.models.sources import Source


class ProjectsSourcesViewSet(
    HtmxMixin,
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
    HtmxDestroyMixin,
    viewsets.GenericViewSet,
):
    """A view set for project sources."""

    lookup_url_kwarg = "source"
    object_name = "source"
    queryset_name = "sources"

    def get_project(self) -> Project:
        """Get the project and check that the user has permission to the perform action."""
        # Only pass on the request `user` so that any source filter query parameters
        # are not applied to projects
        request = HttpRequest()
        request.user = self.request.user
        project = ProjectsViewSet.init(
            self.action, request, self.args, self.kwargs,
        ).get_object()

        if (
            self.action in ["create", "partial_update", "destroy"]
            and project.role
            not in [
                ProjectRole.AUTHOR.name,
                ProjectRole.MANAGER.name,
                ProjectRole.OWNER.name,
            ]
        ) or project.role is None:
            raise exceptions.PermissionDenied

        return project

    def get_queryset(self):
        """Get project sources."""
        project = self.get_project()
        queryset = Source.objects.filter(project=project).select_related(
            "project", "project__account"
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(Q(path__icontains=search))

        return queryset

    def get_object(self, source=None) -> Source:
        """Get a project source."""
        source = source or self.kwargs["source"]
        try:
            return self.get_queryset().filter(id=source)[0]
        except IndexError:
            raise exceptions.NotFound

    def get_serializer_class(self, action=None, source_class: str = None):
        """Get the serializer class for the current action."""
        action = action or self.action
        if action == "create":
            # Call `get_project` to perform permission check
            self.get_project()
            # Get the serializer for the type of source
            source_class = source_class or self.request.data.get("type")
            if source_class is not None:
                cls = SourcePolymorphicSerializer.class_name_serializer_mapping.get(
                    source_class
                )
                if cls is None:
                    raise RuntimeError(
                        "Unhandled source type: {0}".format(source_class)
                    )
                return cls
            raise RuntimeError(
                "Unable to determine source type from '{0}'".format(source_class)
            )
        elif action == "partial_update":
            source = self.get_object()
            return SourcePolymorphicSerializer.model_serializer_mapping[
                source.__class__
            ]
        elif action == "destroy":
            return None
        else:
            return SourcePolymorphicSerializer

    @action(detail=True, methods=["POST"])
    def pull(self, request: Request, *args, **kwargs) -> Response:
        """
        Pull the source.

        Creates a pull job and redirects to the job.
        """
        source = self.get_object()
        job = source.pull(request.user)
        return redirect_to_job(job, accepts_html=self.accepts_html())

    @action(detail=True, methods=["POST"])
    def preview(self, request: Request, *args, **kwargs) -> Response:
        """
        Preview the source.

        Creates a preview job and redirects to the job.
        """
        source = self.get_object()
        job = source.preview(request.user)
        return redirect_to_job(job, accepts_html=self.accepts_html())
