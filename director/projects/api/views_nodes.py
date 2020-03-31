import json
import hashlib

from django.shortcuts import render, get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from projects.models import Project, Node


class NodesCreateRequest(serializers.Serializer):
    """The request data when creating a new node."""

    project = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Project.objects.all(),
        help_text="The project the node is associated with.",
    )

    node = serializers.JSONField(required=True, help_text="The node itself.")

    class Meta:
        model = Node
        fields = ["project", "node"]
        ref_name = None


class NodesCreateResponse(serializers.Serializer):
    """The response data when creating a new node."""

    class Meta:
        model = Node
        fields = ["url"]
        ref_name = None


class NodeSerializer(serializers.Serializer):
    """The response data when creating a new node or retrieving one."""

    node = serializers.JSONField(source="json", help_text="The node itself.")

    class Meta:
        model = Node
        fields = ["url", "project", "node"]
        ref_name = None


class NodesViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):

    lookup_url_kwarg = "cid"

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
        node = serializer.validated_data.get("node")
        jso = json.dumps(node)
        cid = hashlib.sha256(jso.encode("utf-8")).hexdigest()

        # TODO check that the user has write access to the project
        node, created = Node.objects.get_or_create(project=project, cid=cid, json=jso)

        url = node.get_absolute_url()
        return Response({"url": url}, status=status.HTTP_201_CREATED,)

    @swagger_auto_schema(responses={status.HTTP_200_OK: NodeSerializer},)
    def retrieve(self, request: Request, cid: str) -> Response:
        """
        Retrieve a node.

        Performs content negotiation and authorization based on the `Accept` header.
        For `application/json` returns 403 if the request user is not authorized
        to read the project.
        """
        node = get_object_or_404(Node, cid=cid)
        if "application/json" in request.META.get("HTTP_ACCEPT"):
            # TODO: Do authorization based on the `Accept` header and request.user
            serializer = NodeSerializer(node)
            return Response(serializer.data)
        else:
            # TODO: Switch content based user and project.
            # Always have a favicon and a <title> with the type of tag e.g. <title>CodeChunk</title>
            # If not authed (e.g. Google's preview generator) and the project is
            # private don't provide any more content.
            # If authorized, or the project is public, add a <img> with a RPNG of the
            # node - e.g. showing the code behind it.
            # PNG generation is slow suggest / compute intensive so suggest we don't do
            # that at this time e.g. until we know what preview we want to place in it.
            return render(
                request,
                "projects/node.html",
                {"node_type": node_type(node), "node": node},
            )


def node_type(node) -> str:
    """
    Get the type of the node.

    This is a port of https://github.com/stencila/schema/blob/master/ts/util/nodeType.ts
    """
    if isinstance(node, bool):
        return "Boolean"
    if isinstance(node, float):
        return "Number"
    if isinstance(node, str):
        return "Text"
    if isinstance(node, list):
        return "Array"
    node_type = getattr(node, "type", None)
    if node_type is not None:
        return node_type
    return "Object"
