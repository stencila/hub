from typing import Optional

import httpx
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from jobs.api.helpers import redirect_to_job
from jobs.models import Job
from manager.api.authentication import (
    BasicAuthentication,
    CsrfExemptSessionAuthentication,
)
from manager.api.helpers import (
    HtmxCreateMixin,
    HtmxDestroyMixin,
    HtmxListMixin,
    HtmxRetrieveMixin,
)
from projects.api.serializers import SnapshotSerializer
from projects.api.views.projects import get_project
from projects.models.files import File
from projects.models.projects import Project, ProjectRole
from projects.models.snapshots import Snapshot
from users.models import AnonUser

storage_client = httpx.Client()


class ProjectsSnapshotsViewSet(
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

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_permissions(self):
        """
        Get the permissions that the current action requires.

        Override defaults so that `list`, `retrieve` etc do not require
        authentication (although they may raise permission denied
        if not a public project).
        """
        if self.action in ["list", "retrieve", "files", "archive", "session"]:
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
                "creator",
                "creator__personal_account",
                "project",
                "project__account",
                "job",
            )
        )
        return queryset

    def get_object(self, project: Optional[Project] = None) -> Snapshot:
        """Get a project snapshot."""
        try:
            return self.get_queryset(project).get(number=self.kwargs["snapshot"])
        except Snapshot.DoesNotExist:
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
                args=[account.name, project.name, snapshot.number],
            )

    @action(detail=True, methods=["GET"], url_path="files/(?P<path>.*)")
    def files(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a file within a snapshot of the project.

        For `index.html` will add necessary headers and if necessary
        inject content required to connect to a session. For other files
        redirects to the URL for the file (which may be in a
        remote storage bucket for example).
        """
        project = self.get_project()
        snapshot = self.get_object(project)
        path = self.kwargs.get("path") or "index.html"

        try:
            file = File.objects.get(snapshot=snapshot, path=path)
        except File.DoesNotExist:
            raise exceptions.NotFound

        if path != "index.html":
            url = snapshot.file_url(path)
            return redirect(url, permanent=True)

        if isinstance(snapshot.STORAGE, FileSystemStorage):
            # Serve the file from the filesystem.
            # Normally this will only be used during development!
            location = snapshot.file_location(path)
            with snapshot.STORAGE.open(location) as file:
                content = file.read()
        else:
            # Fetch the file from storage and send it on to the client
            url = snapshot.file_url(path)
            content = storage_client.get(url).content

        if not content:
            raise RuntimeError("No content")

        html = content

        # Inject execution toolbar
        source_url = reverse(
            "ui-projects-snapshots-retrieve",
            kwargs=dict(
                account=project.account.name,
                project=project.name,
                snapshot=snapshot.number,
            ),
        )
        session_provider_url = reverse(
            "api-projects-snapshots-session",
            kwargs=dict(project=project.id, snapshot=snapshot.number,),
        )
        toolbar = """
            <stencila-executable-document-toolbar
               source-url="{source_url}"
               session-provider-url="{session_provider_url}"
            >
            </stencila-executable-document-toolbar>
        """.format(
            source_url=source_url, session_provider_url=session_provider_url
        )
        html = html.replace(
            b'data-itemscope="root">', b'data-itemscope="root">' + toolbar.encode()
        )

        response = HttpResponse(html)

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

        The user should have read access to the project.
        Returns a redirect to the URL of the archive.
        """
        snapshot = self.get_object()
        url = snapshot.archive_url()
        return redirect(url)

    @action(detail=True, methods=["post"])
    def session(self, request: Request, *args, **kwargs) -> Response:
        """
        Get a session with the snapshot as the working directory.

        If the user has already created or connected to
        a `session` job for this snapshot, and that job is still running
        then will return that job. Otherwise, will create a new session.
        """
        snapshot = self.get_object()
        try:
            job = Job.objects.filter(
                snapshot=snapshot,
                is_active=True,
                **(
                    {"users": request.user}
                    if request.user.is_authenticated
                    else {"anon_users__id": AnonUser.get_id(request)}
                )
            ).order_by("-created")[0]
        except IndexError:
            job = snapshot.session(request)
            job.dispatch()

        return redirect_to_job(job)
