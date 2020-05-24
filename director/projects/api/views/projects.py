# flake8: noqa F401

from django.db.models import QuerySet, Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    mixins,
    permissions,
    serializers,
    status,
    viewsets,
)
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import AccountUserRole
from general.api.negotiation import IgnoreClientContentNegotiation
from projects.api.serializers import ProjectSerializer, ProjectDestroySerializer
from projects.models import Project, Source
from projects.views.mixins import ProjectPermissionsMixin, ProjectPermissionType


class ProjectCreateRequestSerializer(serializers.ModelSerializer):
    """The request data when creating a project."""

    class Meta:
        model = Project
        fields = ["account", "name", "description", "public"]
        ref_name = None


class ProjectsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    ProjectPermissionsMixin,
):

    # Configuration

    content_negotiation_class = IgnoreClientContentNegotiation
    serializer_class = ProjectSerializer
    project_permission_required = ProjectPermissionType.VIEW

    def get_permissions(self):
        """
        Get the list of permissions that the current action requires.

        - `list` and `retrieve`: auth not required but access denied for private projects
        - `create`: auth required
        """
        return [permissions.IsAuthenticated()] if self.action == "create" else []

    def get_queryset(self) -> QuerySet:
        """Get the projects that the current user has access to."""
        user = self.request.user
        return Project.objects.filter(
            # Project is public, or
            Q(public=True)
            # TODO: Add Qs for other access
        )

    # Views

    def list(self, request: Request) -> Response:
        """
        List projects.

        The optional `q` parameter is a string to search for in project
        `name` and `description`.
        The optional `source` parameter is an address of a
        source within the project.
        Returns a list of projects that the user has access to and which
        matches the supplied filters.
        """
        queryset = self.get_queryset()

        query = self.request.query_params.get("q")
        if query is not None:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        source = self.request.query_params.get("source")
        if source is not None:
            try:
                query = Source.query_from_address(source, prefix="sources")
            except ValueError as exc:
                raise ValidationError({"source": str(exc)})
            queryset = queryset.filter(query)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=ProjectCreateRequestSerializer,
        responses={status.HTTP_201_CREATED: ProjectSerializer},
    )
    def create(self, request: Request) -> Response:
        """
        Create a project.

        Receives details for the new project such as `name` and `description`.
        Returns the details of the created project.
        """
        serializer = ProjectCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account = serializer.validated_data.get("account")
        name = serializer.validated_data.get("name")
        description = serializer.validated_data.get("description")
        public = serializer.validated_data.get("public")

        # TODO: check permissions
        # Check that the user has permissions for the account
        # if not account.permits(request.user, AccountPermissionType.):
        #    raise PermissionDenied

        # for now allow them to create Projects under any account they belong to
        account_roles = AccountUserRole.objects.filter(
            user=self.request.user
        ).select_related("account")

        accounts = [account_role.account for account_role in account_roles]

        if account not in accounts:
            raise PermissionDenied

        project = Project.objects.create(
            account=account,
            name=name,
            description=description,
            creator=request.user,
            public=public,
        )

        serializer = self.get_serializer(project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request: Request, pk: int) -> Response:
        """
        Retrieve a project.

        Returns details of project, including `name` and `description`.
        """
        # Check that the user has VIEW permissions for the project
        project = self.get_project(request.user, pk=pk)
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    def destroy(self, request: Request, pk: int) -> Response:
        """
        Destroy a project.

        Requires the user to be an owner of the project.
        Uses the `ProjectDestroySerializer` to require confirmation
        that the project is to be destroyed.
        """
        project = self.request_permissions_guard(
            request, pk=pk, permission=ProjectPermissionType.OWN
        )

        serializer = ProjectDestroySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["name"] != project.name:
            raise ValidationError("Provided name is not the same as the project name.")

        project.delete()

        return Response()
