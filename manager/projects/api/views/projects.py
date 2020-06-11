from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.shortcuts import reverse
from rest_framework import exceptions, mixins, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

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
    ProjectCreateSerializer,
    ProjectDestroySerializer,
    ProjectListSerializer,
    ProjectRetrieveSerializer,
    ProjectUpdateSerializer,
)
from projects.models import Project, ProjectRole


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

        Actions `list` and `retrive` do not require authentication (although
        the data returned is restricted based on role).
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
        queryset = Project.objects.all().select_related("account")

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                role=RawSQL(
                    """
                       SELECT role
                       FROM projects_projectagent
                       WHERE
                          project_id = projects_project.id AND
                          user_id = %s
                """,
                    [self.request.user.id],
                )
            )

            # Authenticated users can see public projects and those in
            # which they have a role
            queryset = queryset.filter(Q(public=True) | Q(role__isnull=False))

            role = self.request.GET.get("role", "").lower()
            if role == "manager":
                queryset = queryset.filter(role=ProjectRole.MANAGER.name)
            elif role == "owner":
                queryset = queryset.filter(role=ProjectRole.OWNER.name)
        else:
            # Unauthenticated users can only see public projects
            queryset = queryset.filter(public=True).extra(select={"role": "NULL"})

        account = self.request.GET.get("account")
        if account:
            queryset = queryset.filter(account_id=account)

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

        For all actions, uses `get_queryset` to ensure the same access
        restrictions are applied when getting an individual project.

        For `partial-update` and `destroy`, further checks that the user
        is a project MANAGER or OWNER.
        """
        filter = filter_from_ident(self.kwargs["project"])

        account = self.kwargs.get("account")
        if account:
            filter.update(**filter_from_ident(account, prefix="account"))
        elif "id" not in filter:
            raise RuntimeError("Must provide project id if not providing account")

        instance = self.get_queryset().get(**filter)

        if (
            self.action == "partial_update"
            and instance.role not in [ProjectRole.MANAGER.name, ProjectRole.OWNER.name]
        ) or (self.action == "destroy" and instance.role != ProjectRole.OWNER.name):
            raise exceptions.PermissionDenied

        return instance

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.

        For this class, each action has it's own serializer.
        """
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
        
        This should only need to be used for `create`, because for other actions
        it is possible to specify which URL to redirect to using (because the instance
        `id` is already available). ie. use `hx-redirect="UPDATED:{% url ....`
        """
        if self.action in ["create"]:
            project = serializer.instance
            return reverse(
                "ui-projects-retrieve", args=[project.account.name, project.name]
            )
        else:
            return None
