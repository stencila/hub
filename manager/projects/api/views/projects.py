from typing import Dict, List, Optional

from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.shortcuts import reverse
from rest_framework import exceptions, permissions, viewsets
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
    filter_from_ident,
)
from projects.api.serializers import (
    ProjectAgentCreateSerializer,
    ProjectAgentSerializer,
    ProjectAgentUpdateSerializer,
    ProjectCreateSerializer,
    ProjectDestroySerializer,
    ProjectListSerializer,
    ProjectRetrieveSerializer,
    ProjectUpdateSerializer,
)
from projects.models.projects import Project, ProjectAgent, ProjectRole
from users.models import User


def get_projects(user: User):
    """
    Get a queryset of projects for the user.

    Each project is annotated with the role of the user
    for the project.
    """
    if user.is_authenticated:
        # Annotate the queryset with the role of the user
        # Role is the "greater" of the project role and the
        # account role (for the account that owns the project).
        # Authenticated users can see public projects and those in
        # which they have a role
        return Project.objects.annotate(
            role=RawSQL(
                """
SELECT
CASE account_role.role
WHEN 'OWNER' THEN 'OWNER'
WHEN 'MANAGER' THEN
    CASE account_role.role
    WHEN 'OWNER' THEN 'OWNER'
    ELSE 'MANAGER' END
ELSE project_role.role END AS "role"
FROM projects_project AS project
LEFT JOIN
    (SELECT project_id, "role" FROM projects_projectagent WHERE user_id = %s) AS project_role
    ON project.id = project_role.project_id
LEFT JOIN
    (SELECT account_id, "role" FROM accounts_accountuser WHERE user_id = %s) AS account_role
    ON project.account_id = account_role.account_id
WHERE project.id = projects_project.id""",
                [user.id, user.id],
            )
        ).filter(Q(public=True) | Q(role__isnull=False))
    else:
        # Unauthenticated users can only see public projects
        return Project.objects.filter(public=True).extra(select={"role": "NULL"})


def get_project(
    identifiers: Dict[str, str], user: User, roles: Optional[List[ProjectRole]] = None,
):
    """
    Get a project for the user, optionally requiring one or more roles.

    Like GitHub, raises a `NotFound` exception if the user does not have permission
    to avoid leaking the existence of a private project.
    """
    filter = filter_from_ident(identifiers["project"])

    account = identifiers.get("account")
    if account:
        filter.update(**filter_from_ident(account, prefix="account"))
    elif "id" not in filter:
        raise RuntimeError("Must provide project id if not providing account")

    try:
        return get_projects(user).get(
            **filter, **(dict(role__in=[role.name for role in roles]) if roles else {}),
        )
    except Project.DoesNotExist:
        raise exceptions.NotFound


class ProjectsViewSet(
    HtmxMixin,
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
    HtmxDestroyMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for projects.

    Provides basic CRUD views for projects.
    """

    lookup_url_kwarg = "project"
    object_name = "project"
    queryset_name = "projects"

    def get_permissions(self):
        """
        Get the permissions that the current action requires.

        Override defaults so that `list` and `retrive` do not require
        authentication (although the data returned is restricted based on role).
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Get the set of projects that the user has access to and which meet filter criteria.

        TODO: Currently this ignores an authenticated user's access to
              projects inherited from membership of a team.
        """
        queryset = get_projects(self.request.user).select_related("account")

        account = self.request.GET.get("account")
        if account:
            queryset = queryset.filter(account_id=account)

        role = self.request.GET.get("role", "").lower()
        if role == "manager":
            queryset = queryset.filter(role=ProjectRole.MANAGER.name)
        elif role == "owner":
            queryset = queryset.filter(role=ProjectRole.OWNER.name)

        public = self.request.GET.get("public")
        if public:
            if public.lower() in ["false", "no", "0"]:
                queryset = queryset.filter(public=False)
            else:
                queryset = queryset.filter(public=True)

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        # TODO: Find a better way to order role
        return queryset.order_by("-role")

    def get_object(self):
        """
        Get the project.

        For `partial-update` and `destroy`, further checks that the user
        is a project MANAGER or OWNER.
        """
        project = get_project(self.kwargs, self.request.user)

        if (
            self.action == "partial_update"
            and project.role not in [ProjectRole.MANAGER.name, ProjectRole.OWNER.name]
        ) or (self.action == "destroy" and project.role != ProjectRole.OWNER.name):
            raise exceptions.PermissionDenied

        return project

    def get_serializer_class(self):
        """Get the serializer class for the current action."""
        try:
            return {
                "list": ProjectListSerializer,
                "create": ProjectCreateSerializer,
                "retrieve": ProjectRetrieveSerializer,
                "partial_update": ProjectUpdateSerializer,
                "destroy": ProjectDestroySerializer,
            }[self.action]
        except KeyError:
            raise RuntimeError("Unexpected action {}".format(self.action))

    def get_success_url(self, serializer):
        """
        Get the URL to use in the Location header when an action is successful.

        For `create`, redirects to the "main" page for the project.
        """
        if self.action in ["create"]:
            project = serializer.instance
            return reverse(
                "ui-projects-retrieve", args=[project.account.name, project.name]
            )
        else:
            return None

    @action(detail=True, methods=["POST"])
    def pull(self, request: Request, *args, **kwargs) -> Response:
        """
        Pull the project.

        Creates a pull job and redirects to it.
        """
        project = self.get_object()
        job = project.pull(request.user)
        job.dispatch()
        return redirect_to_job(job, accepts_html=self.accepts_html())


class ProjectsAgentsViewSet(
    HtmxMixin,
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
    HtmxDestroyMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for projects agents (users or teams).

    Provides basic CRUD views for project agents.

    Uses `ProjectsViewSet.get_object` so that we can obtain the
    role of the user for the project (including inherited role from the account).
    """

    lookup_url_kwarg = "agent"
    object_name = "agent"
    queryset_name = "agents"

    def get_project(self) -> Project:
        """Get the project and check that the user has permission to the perform action."""
        project = ProjectsViewSet.init(
            self.action, self.request, self.args, self.kwargs
        ).get_object()

        if (
            self.action in ["create", "partial_update", "destroy"]
            and project.role not in [ProjectRole.MANAGER.name, ProjectRole.OWNER.name]
        ) or project.role is None:
            raise exceptions.PermissionDenied

        return project

    def get_queryset(self):
        """Get project agents."""
        project = self.get_project()
        return ProjectAgent.objects.filter(project=project)

    def get_object(self) -> ProjectAgent:
        """Get a project agent."""
        try:
            return self.get_queryset().filter(id=self.kwargs["agent"])[0]
        except IndexError:
            raise exceptions.NotFound

    def get_serializer_class(self):
        """Get the serializer class for the current action."""
        if self.action == "create":
            # Call `get_project` to perform permission check
            self.get_project()
            return ProjectAgentCreateSerializer
        elif self.action == "partial_update":
            return ProjectAgentUpdateSerializer
        elif self.action == "destroy":
            return None
        else:
            return ProjectAgentSerializer

    def get_response_context(self, **kwargs):
        """Override to provide additional context when rendering templates."""
        return super().get_response_context(
            queryset=self.get_queryset(), project=self.get_project(), **kwargs
        )
