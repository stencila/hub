from typing import List, Optional

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
from projects.api.serializers import SnapshotSerializer
from projects.api.views.projects import ProjectsViewSet, get_project
from projects.models.projects import Project, ProjectRole
from projects.models.snapshots import Snapshot


class ProjectsSnapshotsViewSet(
    HtmxMixin,
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxRetrieveMixin,
    HtmxDestroyMixin,
    viewsets.GenericViewSet,
):
    """A view set for project snapshots."""

    lookup_url_kwarg = "snapshot"
    object_name = "snapshot"
    queryset_name = "snapshots"

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
        """Get project snapshots."""
        project = project or self.get_project()
        queryset = (
            Snapshot.objects.filter(project=project)
            .order_by("-created")
            .select_related(
                "creator", "creator__personal_account", "project", "project__account"
            )
        )
        return queryset

    def get_object(self):
        """Get a project snapshot."""
        try:
            return self.get_queryset().filter(id=self.kwargs["snapshot"])[0]
        except IndexError:
            raise exceptions.NotFound

    def get_serializer_class(self):
        """Get the serializer class for the current action."""
        return SnapshotSerializer

    def get_success_url(self, serializer):
        """
        Get the URL to use in the Location header when an action is successful.

        For `create`, redirects to the page for the snapshot.
        """
        if self.action in ["create"]:
            snapshot = serializer.instance
            project = snapshot.project
            account = project.account
            return reverse(
                "ui-projects-snapshots-retrieve",
                args=[account.name, project.name, snapshot.id],
            )
