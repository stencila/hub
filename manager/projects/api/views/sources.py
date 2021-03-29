from typing import Optional

from django.conf import settings
from django.db.models import F, Q
from django.shortcuts import redirect, reverse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from jobs.api.helpers import redirect_to_job
from manager.api.helpers import (
    HtmxCreateMixin,
    HtmxDestroyMixin,
    HtmxListMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
)
from projects.api.serializers import SourcePolymorphicSerializer, SourceSerializer
from projects.api.views.projects import get_project
from projects.models.projects import Project, ProjectRole
from projects.models.providers import GithubRepo
from projects.models.sources import Source
from users.socialaccount.tokens import get_user_google_token


class ProjectsSourcesViewSet(
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
        The `event` action also does not require authentication so
        that source providers such as Google can post event notifications.
        """
        if self.action in ["list", "retrieve", "open", "event"]:
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
        queryset = (
            manager.filter(project=project)
            .select_related("project", "project__account")
            .order_by(F("order").desc(nulls_last=True), "updated")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(address__icontains=search) | Q(path__icontains=search)
            )

        return queryset

    def get_object(self, project: Optional[Project] = None) -> Source:
        """
        Get a source for the project.

        The `source` URL kwarg can be an integer id or address
        """
        source = self.kwargs["source"]
        try:
            identifier = dict(id=int(source))
        except ValueError:
            identifier = dict(address=source)
        try:
            return self.get_queryset(project).get(**identifier)
        except Source.DoesNotExist:
            raise exceptions.NotFound

    def get_serializer_class(self, action=None, source_class: str = None):
        """Get the serializer class for the current action."""
        action = action or self.action
        if action == "list":
            # Use the base serializer class which gives the type
            # of the source
            return SourceSerializer
        elif action == "destroy":
            return None
        elif getattr(self, "swagger_fake_view", False):
            # For API Schema generation return the polymorphic serializer
            # instead of dynamically determined, class specific serializer
            # as below for `create` and `partial_update`
            return SourcePolymorphicSerializer
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
                    raise exceptions.ValidationError(
                        dict(type="Unknown source type: {0}".format(source_class))
                    )
                return cls
            return SourcePolymorphicSerializer
        elif action == "partial_update":
            source = self.get_object()
            return SourcePolymorphicSerializer.model_serializer_mapping[
                source.__class__
            ]
        else:
            return SourcePolymorphicSerializer

    def get_response_context(self, *args, source_class: str = None, **kwargs):
        """
        Add project to the response context for templates.

        The `project` is added because some templates need to use `project.role`
        for source actions (`role` is not available via `source.project`).
        """
        context = super().get_response_context(*args, **kwargs)
        context["source_class"] = source_class
        context["project"] = self.get_project()

        if self.action == "create":
            source_class = source_class or self.request.data.get("type")
            if source_class == "GithubSource":
                context["github_repos"] = GithubRepo.objects.filter(
                    user=self.request.user
                )
            elif source_class.startswith("Google"):
                token, app = get_user_google_token(self.request.user)
                if app:
                    context["app_id"] = app.client_id.split("-")[0]
                    context["client_id"] = app.client_id
                    context["developer_key"] = settings.GOOGLE_API_KEY
                if token:
                    context["access_token"] = token.token
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

    # Most of the following views serve simply to provide docstrings
    # from which API documentation is generated.

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="A string to search for in the source's `path`.",
                type=openapi.TYPE_STRING,
            )
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List a project's sources.

        Returns a list of sources in the project.
        The returned list can be filtered using the query parameter, `search` which matches
        against the source's `path` string.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a project source.

        Receives details of the source. This should include the `type` of source, a string matching
        one of the implemented source classes e.g. `ElifeSource`, `GoogleDocsSource`, `GithubSource`
        as well as the destination `path`, and other type specific properties.
        See https://github.com/stencila/hub/blob/master/manager/projects/models/sources.py.

        For example, to create a new source for a Google Doc:

        ```json
        {
            "type": "GoogleDocsSource",
            "path": "report.gdoc",
            "docId": "1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA"
        }
        ```

        Alternatively, if the request includes a `url`, then the type will be inferred from
        the URL, falling back to a `UrlSource`. For example, the create the above Google Doc:

        ```json
        {
            "url": "https://docs.google.com/document/u/1/d/1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA/edit"
            "path": "report.gdoc",
        }
        ```

        Returns details of the new source.
        """
        url = request.data.get("url")
        if url:
            try:
                address = Source.coerce_address(url)
            except ValueError:
                pass  # URL could not be coerced into a source address
            else:
                if address:
                    request.data.copy().update(**address, type=address.type.__name__)

        return super().create(request, *args, **kwargs)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a project source.

        Returns details of the source.
        """
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update a project source.

        Receives details of the source.
        Returns updated details of the source.
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Destroy a project source.

        Removes the source from the project.
        Returns an empty response on success.
        """
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["GET"], url_path="open/?(?P<path>.+)?")
    def open(self, request: Request, *args, **kwargs) -> Response:
        """
        Open a project source, or a file within it.

        Returns a redirect response to an external URL.
        """
        source = self.get_object()
        return redirect(source.get_url(path=self.kwargs.get("path")))

    @action(detail=True, methods=["POST"])
    def pull(self, request: Request, *args, **kwargs) -> Response:
        """
        Pull a project source.

        Creates a pull job and redirects to it.
        """
        source = self.get_object()
        job = source.pull(request.user)
        job.dispatch()
        return redirect_to_job(job, accepts_html=self.accepts_html())

    @action(detail=True, methods=["POST"])
    def watch(self, request: Request, *args, **kwargs) -> Response:
        """
        Watch a project source.

        Creates a subscription to listen to events for the source.
        Returns an empty response on success. Returns a 405 if the
        source type does not support watches.
        """
        source = self.get_object()
        try:
            source.watch(request.user)
        except PermissionError as exc:
            raise exceptions.PermissionDenied(exc)
        except NotImplementedError:
            raise exceptions.MethodNotAllowed(
                "POST",
                f"Watching a source of type {source.__class__.__name__} is not supported.",
            )
        return Response()

    @action(detail=True, methods=["POST"])
    def unwatch(self, request: Request, *args, **kwargs) -> Response:
        """
        Unwatch a project source.

        Removes any subscription to listen to events for the source.
        Returns an empty response on success (including if the source
        was not being watched before the request).
        """
        source = self.get_object()
        try:
            source.unwatch(request.user)
        except NotImplementedError:
            pass
        return Response()

    @action(detail=True, methods=["POST"])
    def event(self, request: Request, *args, **kwargs) -> Response:
        """
        Receive an event notification for a project source.

        Receives event data from a source provider (e.g. Github, Google)
        and forward's it on to the source's event handler.
        Returns an empty response.
        """
        # This method allows for posting events for private projects
        # so bypasses the `get_object` method. The following approach
        # is also more DB query efficient which is important for
        # this high volume endpoint.
        source = Source.objects.select_related("project").get(
            project_id=self.kwargs["project"], id=self.kwargs["source"]
        )
        try:
            source.event(data=self.request.data, headers=self.request.headers)
        except PermissionError as exc:
            raise exceptions.PermissionDenied(exc)
        return Response()
