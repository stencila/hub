import json
from typing import Optional

import pygments
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from pygments.formatters import HtmlFormatter
from pygments.lexers.data import JsonLexer
from pygments.lexers.markup import TexLexer
from pygments.lexers.special import TextLexer
from rest_framework import mixins, parsers, permissions, renderers, status, viewsets
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.request import Request
from rest_framework.response import Response
from stencila.schema.util import node_type as schema_node_type

from projects.api.serializers import (
    NodeCreateRequest,
    NodeCreateResponse,
    NodeSerializer,
)
from projects.models.nodes import Node
from projects.models.projects import Project, ProjectRole
from users.models import get_projects


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
        request_body=NodeCreateRequest,
        responses={status.HTTP_201_CREATED: NodeCreateResponse},
    )
    def create(self, request: Request) -> Response:
        """
        Create a node.

        Receives a request with the `node` (as JSON) and possibly other information
        e.g. the `project` the node is associated with, the `app` it was

        Returns the URL of the node.
        """
        serializer = NodeCreateRequest(data=request.data)
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

        # Create the node
        try:
            node = Node.objects.create(
                creator=request.user, project=project, app=app, host=host, json=node
            )
        except IntegrityError:
            raise ValidationError(dict(key="Attempting to create a duplicate key"))

        serializer = NodeCreateResponse(node, context={"request": request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            # Most of the time this action will requested with `Accept: application/json`.
            # However, in case it is not, `template_name` is required.
            template_name="projects/nodes/retrieve.html",
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

        - For `text/html` (and others) returns a HTML rendering of the
        of the node without authorization checking; this is to allow scrapers such
        as Google Docs link preview generator to be able to fetch basic information
        on the node. For private projects node URLs should be kept private to avoid
        unauthorized access.
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
            # Return a HTML representation of the node
            node_type = schema_node_type(node.json)
            if node_type in ("CodeChunk", "CodeExpression"):
                lang = node.json.get("programmingLanguage", "")
                try:
                    lexer = pygments.lexers.get_lexer_by_name(lang)
                except pygments.util.ClassNotFound:
                    lexer = TextLexer()
                code = node.json.get("text", "")
            elif node_type in ("MathBlock", "MathFragment"):
                lexer = TexLexer()
                code = node.json.get("text")
            else:
                lexer = JsonLexer()
                code = json.dumps(node.json, indent=2)

            formatter = HtmlFormatter(cssclass="source", style="colorful")
            css = formatter.get_style_defs(".source")
            html = pygments.highlight(code, lexer, formatter)

            app_name, app_url = node.get_app()

            return Response(
                dict(
                    meta=node.get_meta(),
                    node=node,
                    css=css,
                    html=html,
                    app_name=app_name,
                    app_url=app_url,
                ),
                template_name="projects/nodes/retrieve.html",
            )
