from typing import Optional
import hashlib
import json

from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, serializers, status, viewsets, renderers
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from lib.converter_facade import (
    ConverterFacade,
    ConverterIo,
    ConverterIoType,
    ConverterContext,
)
from lib.conversion_types import ConversionFormatId
from projects.models import Node
from projects.views.mixins import ProjectPermissionsMixin, ProjectPermissionType

# Applications known to create nodes
# For these provide further details in HTML views of nodes
APPS = {
    "encoda": ("Stencila Encoda", "https://github.com/stencila/encoda#readme"),
    "gsuita": (
        "Stencila for GSuite",
        "https://gsuite.google.com/marketplace/app/stencila/110435422451",
    ),
}


class NodesCreateRequest(serializers.ModelSerializer):
    """The request data when creating a new node."""

    node = serializers.JSONField(required=True, help_text="The node itself.")

    class Meta:
        model = Node
        fields = ["project", "app", "host", "node"]
        ref_name = None


class NodesCreateResponse(serializers.ModelSerializer):
    """The response data when creating a new node."""

    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.get_absolute_url())

    class Meta:
        model = Node
        fields = ["key", "url"]
        ref_name = None


class NodeSerializer(NodesCreateResponse):
    """The response data when retrieving a node."""

    node = serializers.JSONField(source="json", help_text="The node itself.")

    class Meta:
        model = Node
        fields = ["project", "app", "host", "key", "url", "node"]
        ref_name = None


class NodesViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    ProjectPermissionsMixin,
):

    lookup_url_kwarg = "key"
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]

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
        app = serializer.validated_data.get("app")
        host = serializer.validated_data.get("host")
        node = serializer.validated_data.get("node")

        # Check that the user has EDIT permissions for the project
        if not self.is_permitted(
            request.user, ProjectPermissionType.EDIT, pk=project.id
        ):
            raise PermissionDenied

        fingerprint = "{}-{}-{}-{}".format(project, app, host, json.dumps(node))
        key = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()

        # Get (efficiently, if it exists), or create, the node
        try:
            node = Node.objects.get(key=key)
        except Node.DoesNotExist:
            node = Node.objects.create(
                key=key, project=project, app=app, host=host, json=node
            )

        serializer = NodesCreateResponse(node, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED,)

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
        accept = request.META.get("HTTP_ACCEPT")
        if format == "json" or (accept and "application/json" in accept):
            # Require the user is authenticated and has VIEW permissions for the project
            if not request.user.is_authenticated:
                raise NotAuthenticated
            if not self.is_permitted(
                request.user, ProjectPermissionType.VIEW, pk=node.project.id
            ):
                raise PermissionDenied

            serializer = NodeSerializer(node, context={"request": request})
            return Response(serializer.data)
        else:
            # Return a basic view if the user does NOT have VIEW permissions.
            if not self.is_permitted(
                request.user, ProjectPermissionType.VIEW, pk=node.project.id
            ):
                return Response(
                    {"node_type": node_type(node.json), "node": node},
                    template_name="projects/node_basic.html",
                )

            # Return a more complete view if the user has VIEW permissions.
            # This should include public projects.
            try:
                # Currently allow this to fail if the converter binary
                # can not be found e.g. during CI testing
                conversion = ConverterFacade(settings.STENCILA_BINARY).convert(
                    input_data=ConverterIo(
                        ConverterIoType.PIPE,
                        json.dumps(node.json).encode("utf8"),
                        ConversionFormatId.json,
                    ),
                    output_data=ConverterIo(
                        ConverterIoType.PIPE, None, ConversionFormatId.html
                    ),
                    context=ConverterContext(standalone=False),
                )
                html = conversion.stdout.decode("utf8")
            except FileNotFoundError:
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
                template_name="projects/node_complete.html",
            )


def node_type(node) -> str:
    """
    Get the type of the node.

    This is a port of https://github.com/stencila/schema/blob/master/ts/util/nodeType.ts
    """
    if node is None:
        return "Null"
    if isinstance(node, bool):
        return "Boolean"
    if isinstance(node, int) or isinstance(node, float):
        return "Number"
    if isinstance(node, str):
        return "Text"
    if isinstance(node, list) or isinstance(node, tuple):
        return "Array"
    if isinstance(node, dict):
        node_type = node.get("type")
        if node_type is not None:
            return node_type
    return "Object"
