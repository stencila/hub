from typing import Optional

from django.db.models import Q
from django.shortcuts import reverse
from rest_framework import permissions, viewsets
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
from projects.api.serializers import SourcePolymorphicSerializer, SourceSerializer
from projects.api.views.projects import get_project
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
        Get the project and check that the user has permission for the current action.
        """
        if not hasattr(self, "project"):
            self.project = get_project(
                self.kwargs,
                self.request.user,
                [ProjectRole.AUTHOR, ProjectRole.MANAGER, ProjectRole.OWNER]
                if self.action in ["create", "partial_update", "destroy"]
                else None,
            )
        return self.project

    def get_queryset(self, project: Optional[Project] = None):
        """
        Get sources for the project.

        For `list` action uses the base object manager to avoid
        making additional database queries for each source type.
        """
        manager = Source.objects_base if self.action == "list" else Source.objects

        project = project or self.get_project()
        queryset = manager.filter(project=project).select_related(
            "project", "project__account"
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(Q(path__icontains=search))

        return queryset

    def get_object(self, project: Optional[Project] = None) -> Source:
        """Get a source for the project."""
        return self.get_queryset(project).get(id=self.kwargs["source"])

    def get_serializer_class(self, action=None, source_class: str = None):
        """Get the serializer class for the current action."""
        action = action or self.action
        if action == "list":
            # Use the base serializer class which gives the type
            # of the source
            return SourceSerializer
        elif action == "create":
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

    def get_response_context(self, *args, **kwargs):
        """
        Add project to the response context for templates.

        Done because some templates need to use `project.role`
        for source actions (`role` is not available via `source.project`).
        """
        context = super().get_response_context(*args, **kwargs)
        context["project"] = self.get_project()
        return context

    def get_success_url(self, serializer):
        """
        Get the URL to use in the Location header when an action is successful.

        For `create`, redirects to the new source.
        """
        if self.action in ["create"]:
            project = self.get_project()
            return reverse(
                "ui-projects-sources-retrieve",
                args=[project.account.name, project.name, serializer.instance.id],
            )
        else:
            return None

    @action(detail=True, methods=["POST"])
    def pull(self, request: Request, *args, **kwargs) -> Response:
        """
        Pull the source.

        Creates a pull job and redirects to it.
        """
        source = self.get_object()
        job = source.pull(request.user)
        return redirect_to_job(job, accepts_html=self.accepts_html())
