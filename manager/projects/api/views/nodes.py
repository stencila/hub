import secrets
from typing import Optional

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, parsers, permissions, renderers, status, viewsets
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from stencila.schema.util import node_type

from projects.api.serializers import (
    NodesCreateRequest,
    NodesCreateResponse,
    NodeSerializer,
)
from projects.api.views.projects import get_projects
from projects.models.nodes import Node
from projects.models.projects import Project, ProjectRole

# Applications known to create nodes
# For these provide further details in HTML views of nodes
APPS = {
    "api": ("Stencila Hub API", "https://hub.stenci.la/api"),
    "encoda": ("Stencila Encoda", "https://github.com/stencila/encoda#readme"),
    "gsuita": (
        "Stencila for GSuite",
        "https://gsuite.google.com/marketplace/app/stencila/110435422451",
    ),
}


class NodesViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    A view set for nodes.

    Provides create and retrieve views for nodes.
    """

    lookup_url_kwarg = "key"

    # Use the plain `JSONParser`, rather than the default
    # `CamelCaseJSONParser` so that camelCased properties within
    # a node are not transformed to snake case.
    parser_classes = [parsers.JSONParser]

    # Use `TemplateHTMLRenderer` as the default renderer so that
    # bots that `Accept` anything get HTML that rather than JSON.
    # For why this ordering is important see
    # https://www.django-rest-framework.org/api-guide/renderers/#ordering-of-renderer-classes
    renderer_classes = [renderers.TemplateHTMLRenderer, renderers.JSONRenderer]

    def get_permissions(self):
        """
        Get the list of permissions that the current action requires.

        - `create` (i.e. POST) required authentication to prevent unauthenticated
          users using this view set as a key/value store
        - `retrieve` (i.e. GET) does not require authentication (although content
          will be limited in that case)
        """
        if self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        request_body=NodesCreateRequest,
        responses={status.HTTP_201_CREATED: NodesCreateResponse},
    )
    def create(self, request: Request) -> Response:
        """
        Create a node.

        Receives a request with the `node` and other information e.g. `project`.
        Returns the URL of the node.
        """
        serializer = NodesCreateRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = serializer.validated_data.get("project")
        app = serializer.validated_data.get("app", "api")
        host = serializer.validated_data.get("host")
        node = serializer.validated_data.get("node")

        # Check that the user has EDIT permissions for the project,
        # if provided.
        if project:
            try:
                get_projects(request.user).get(
                    id=project.id,
                    role__in=[
                        role.name for role in ProjectRole.and_above(ProjectRole.AUTHOR)
                    ],
                )
            except Project.DoesNotExist:
                raise PermissionDenied

        # Create the node with a unique key
        node = Node.objects.create(
            creator=request.user,
            key=secrets.token_hex(32),
            project=project,
            app=app,
            host=host,
            json=node,
        )

        serializer = NodesCreateResponse(node, context={"request": request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            # Most of the time this action will requested with `Accept: application/json`.
            # However, in case it is not, `template_name` is required.
            template_name="projects/nodes/complete.html",
        )

    @swagger_auto_schema(responses={status.HTTP_200_OK: NodeSerializer},)
    def retrieve(
        self, request: Request, key: str, format: Optional[str] = None
    ) -> Response:
        """
        Retrieve a node.

        Performs content negotiation and authorization based on the `Accept` header.

        - For `application/json` returns 403 if the request user is not authorized
        to read the project.
        - For `text/html` (and others) returns a very simple HTML rendering of the
        of the node (only type etc) if the user does not have read access to the project.
        Otherwise, should return a full HTML rendering of the node using Encoda.
        """
        node = get_object_or_404(Node, key=key)
        if format == "json" or request.accepted_renderer.format == "json":
            # Require the user is authenticated and has VIEW permissions for the project
            if not request.user.is_authenticated:
                raise NotAuthenticated
            if node.project:
                try:
                    get_projects(request.user).get(id=node.project.id)
                except Project.DoesNotExist:
                    raise PermissionDenied

            serializer = NodeSerializer(node, context={"request": request})
            return Response(serializer.data)
        else:
            # Return a basic view if the user does NOT have permission to view
            # the project that the node belongs to.
            if node.project:
                try:
                    get_projects(request.user).get(id=node.project.id)
                except Project.DoesNotExist:
                    return Response(
                        {"node_type": node_type(node.json), "node": node},
                        template_name="projects/nodes/basic.html",
                    )

            # Return a more complete view if the user has VIEW permissions.
            # This should include public projects.
            # TODO: generate and cache a HTML representation of the node using a job
            html = ""

            app_name, app_url = APPS.get(node.app, (node.app, None))
            return Response(
                {
                    "node_type": node_type(node.json),
                    "app_url": app_url,
                    "app_name": app_name,
                    "node": node,
                    "html": html,
                },
                template_name="projects/nodes/complete.html",
            )
