from typing import Optional

from django.http import FileResponse
from django.shortcuts import get_object_or_404, reverse
from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from manager.api.helpers import (
    HtmxCreateMixin,
    HtmxDestroyMixin,
    HtmxListMixin,
    HtmxMixin,
    HtmxRetrieveMixin,
)
from projects.api.serializers import SnapshotSerializer
from projects.api.views.projects import get_project
from projects.models.files import File
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

    def get_permissions(self):
        """
        Get the permissions that the current action requires.

        Override defaults so that `list` and `retrieve` do not require
        authentication (although they may raise permission denied
        if not a public project).
        """
        if self.action in ["list", "retrieve", "files"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

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

    def get_object(self, project: Optional[Project] = None):
        """Get a project snapshot."""
        try:
            return self.get_queryset(project).filter(id=self.kwargs["snapshot"])[0]
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

    @action(detail=True, methods=["get"], url_path="(?P<path>.+)")
    def files(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a file within a snapshot of the project.

        Returns the content of the file, as is. Use the `download` parameter to
        force `Content-Disposition: attachment`.
        """
        snapshot = self.get_object()
        path = self.kwargs.get("path")

        # Get the files from the snapshot or 404
        try:
            file = File.objects.get(snapshot=snapshot, path=path)
        except File.DoesNotExist:
            raise exceptions.NotFound

        # Get the absolute path to the file.
        absolute_path = snapshot.get_file_path(path)

        # Return "binary" files as attachments with mimetype is determined automatically from
        # the files extension.
        as_attachment = "download" in request.query_params

        response = FileResponse(
            open(absolute_path, "rb"),
            content_type=file.mimetype,
            as_attachment=as_attachment,
        )

        # Add headers if the account has `hosts` set
        hosts = snapshot.project.account.hosts
        if hosts:
            # CSP `frame-ancestors` for modern browers
            response["Content-Security-Policy"] = "frame-ancestors 'self' {};".format(
                hosts
            )
            # `X-Frame-Options` for older browsers (only allows one value)
            host = hosts.split()[0]
            response["X-Frame-Options"] = "allow-from {}".format(host)
        else:
            response["Content-Security-Policy"] = "frame-ancestors 'self';"
            response["X-Frame-Options"] = "sameorigin"

        return response

    @action(detail=True, methods=["get"])
    def archive(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve an archive for a project snapshot.
        """
        snapshot = self.get_object()

        absolute_path = snapshot.get_archive_path()

        return FileResponse(open(absolute_path, "rb"), as_attachment=True,)
