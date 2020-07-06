from typing import List, Optional

from django.db.models import Prefetch, Q
from django.db.models.expressions import RawSQL
from django.shortcuts import reverse
from rest_framework import exceptions, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.api.serializers import (
    AccountCreateSerializer,
    AccountListSerializer,
    AccountRetrieveSerializer,
    AccountTeamCreateSerializer,
    AccountTeamDestroySerializer,
    AccountTeamSerializer,
    AccountTeamUpdateSerializer,
    AccountUpdateSerializer,
    AccountUserCreateSerializer,
    AccountUserSerializer,
)
from accounts.models import Account, AccountRole, AccountTeam, AccountUser
from accounts.quotas import AccountQuotas
from manager.api.helpers import (
    HtmxCreateMixin,
    HtmxListMixin,
    HtmxMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
    filter_from_ident,
)
from users.api.serializers import UserIdentifierSerializer
from users.models import User


def get_account(
    identifier: str, user: User, roles: Optional[List[AccountRole]] = None,
):
    """
    Get an account for the user, optionally requiring one or more roles.
    """
    try:
        return Account.objects.get(
            **filter_from_ident(identifier),
            **(dict(users__user=user) if user else {}),
            **(dict(users__role__in=[role.name for role in roles]) if roles else {}),
        )
    except Account.DoesNotExist:
        raise exceptions.PermissionDenied


class AccountsViewSet(
    HtmxMixin,
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxRetrieveMixin,
    HtmxUpdateMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for accounts.

    Provides basic account CRU(D) views for accounts.
    """

    lookup_url_kwarg = "account"
    object_name = "account"
    queryset_name = "accounts"

    def get_permissions(self):
        """
        Get the permissions that the current action requires.

        Actions `list` and `retrive` do not require authentication (although
        the data returned is restricted).
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Get the queryset for the current action.

        For `list`, returns **all** accounts (i.e. the
        list of accounts is treated as public).
        """
        queryset = Account.objects.all()

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                role=RawSQL(
                    """
                       SELECT role FROM accounts_accountuser
                       WHERE
                          account_id = accounts_account.id AND
                          user_id = %s
                """,
                    [self.request.user.id],
                )
            )

            role = self.request.GET.get("role", "").lower()
            if role == "member":
                queryset = queryset.filter(role__isnull=False)
            elif role == "manager":
                queryset = queryset.filter(role=AccountRole.MANAGER.name)
            elif role == "owner":
                queryset = queryset.filter(role=AccountRole.OWNER.name)
        else:
            queryset = queryset.extra(select={"role": "NULL"})

        search = self.request.GET.get("search", None)
        if search is not None:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(display_name__icontains=search)
            )

        isa = self.request.GET.get("is", None)
        if isa == "user":
            queryset = queryset.filter(user__isnull=False)
        elif isa == "org":
            queryset = queryset.filter(user__isnull=True)

        # TODO: Find a better way to order role so MANAGER is before MEMBER
        return queryset.order_by("-role")

    def get_object(self):
        """
        Get the object for the current action.

        For `retrieve`, prefetches related data.

        For `partial_update` checks that the useris an account MANAGER or OWNER.
        Only OWNER is permitted to `update_plan` or `destroy`.
        """
        ident = self.kwargs["account"]
        queryset = self.get_queryset().filter(**filter_from_ident(ident))

        if self.action in ["retrieve", "partial_update"]:
            # The API `AccountRetrieveSerializer` uses nested serializers
            # for `teams` and `users`. Also, the UI `update` view uses the
            # number of teams and users in the side bar.
            # So we use `prefetch_related` to reduce the number of DB queries
            filter = filter_from_ident(ident, prefix="account")
            queryset = queryset.prefetch_related(
                Prefetch(
                    "teams",
                    queryset=AccountTeam.objects.filter(**filter).prefetch_related(
                        "members"
                    ),
                ),
                Prefetch(
                    "users",
                    queryset=AccountUser.objects.filter(**filter).select_related(
                        "user"
                    ),
                ),
            )

        try:
            # Using [0] adds LIMIT 1 to query so is more efficient than `.get(**filter)`
            instance = queryset[0]
        except IndexError:
            raise exceptions.NotFound

        if (
            self.action == "partial_update"
            and instance.role not in [AccountRole.MANAGER.name, AccountRole.OWNER.name]
        ) or (
            self.action in ("update_plan", "destroy")
            and instance.role != AccountRole.OWNER.name
        ):
            raise exceptions.PermissionDenied

        return instance

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.

        For this class, each action has it's own serializer.
        """
        try:
            return {
                "list": AccountListSerializer,
                "create": AccountCreateSerializer,
                "retrieve": AccountRetrieveSerializer,
                "update": AccountUpdateSerializer,
                "partial_update": AccountUpdateSerializer,
            }[self.action]
        except KeyError:
            raise RuntimeError("Unexpected action {}".format(self.action))

    def get_success_url(self, serializer):
        """
        Get the URL to use in the Location header when an action is successful.

        For `create`, redirects to the "projects" page for the organization
        to encourage them to create a project for it.

        This should only need to be used for `create`, because for other actions
        it is possible to directly specify which URL to redirect to (because the instance
        `id` is already available). ie. use `hx-redirect="UPDATED:{% url ....`
        """
        if self.action in ["create"]:
            return reverse("ui-accounts-retrieve", args=[serializer.instance.name])
        else:
            return None

    @action(detail=True, methods=["PATCH"])
    def update_plan(self):
        raise NotImplementedError()


class AccountsUsersViewSet(
    HtmxMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for account users.

    Provides basic CRUD views for account users.
    """

    # Configuration

    lookup_url_kwarg = "user"

    def get_account(self):  # noqa: D102
        try:
            account = Account.objects.get(
                **filter_from_ident(self.kwargs["account"]),
                users__user=self.request.user,
                users__role__in=[
                    AccountRole.MEMBER.name,
                    AccountRole.MANAGER.name,
                    AccountRole.OWNER.name,
                ]
                if self.action in ["list", "retrieve"]
                else [AccountRole.MANAGER.name, AccountRole.OWNER.name],
            )
        except Account.DoesNotExist:
            raise exceptions.PermissionDenied

        if self.action == "create":
            AccountQuotas.USERS.check(account)

        return account

    def get_account_role(self):  # noqa: D102
        account = self.get_account()
        role = account.users.get(user=self.request.user).role
        return account, role

    def get_queryset(self, account=None):
        """Get the queryset."""
        if account is None:
            account = self.get_account()
        return AccountUser.objects.filter(account=account)

    def get_object(self, account=None):
        """Get the object."""
        if account is None:
            account = self.get_account()
        try:
            return AccountUser.objects.get(
                account=account,
                **filter_from_ident(
                    self.kwargs["user"], prefix="user", str_key="username"
                ),
            )
        except AccountUser.DoesNotExist:
            raise exceptions.NotFound

    def get_serializer_class(self):  # noqa: D102
        return (
            AccountUserCreateSerializer
            if self.action == "create"
            else AccountUserSerializer
        )

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Add an account user.

        Returns data for the new account user.
        """
        account, role = self.get_account_role()
        serializer = self.get_serializer(data=request.data)

        # TODO: Check that the user is not already an account user

        if self.accepts_html():
            if serializer.is_valid():
                serializer.save()
                status = self.CREATED
            else:
                status = self.INVALID

            return Response(dict(account=account, role=role), status=status)
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=self.CREATED)

    def partial_update(
        self, request: Request, *args, **kwargs
    ) -> Response:  # noqa: D102
        account, role = self.get_account_role()
        account_user = self.get_object()
        serializer = self.get_serializer(account_user, data=request.data, partial=True)

        if self.accepts_html():
            if serializer.is_valid():
                serializer.save()
                status = self.UPDATED
            else:
                status = self.INVALID
            return Response(dict(account=account, role=role), status=status)
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=self.UPDATED)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Remove an account user.

        Returns an empty response.
        """
        account, role = self.get_account_role()
        account_user = self.get_object()

        # TODO: Check that there is at least one admin left on the account

        account_user.delete()
        if self.accepts_html():
            return Response(dict(account=account, role=role), status=self.DESTROYED)
        else:
            return Response(status=self.DESTROYED)


class AccountsTeamsViewSet(
    HtmxMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for account teams.

    Provides basic team CRUD views.
    """

    # Configuration

    lookup_url_kwarg = "team"

    def get_permissions(self):
        """
        Get the permissions that the current action requires.

        Requires authentication for all actions (i.e. no public access).
        """
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.

        For `create`, checks that the user is an account MANAGER
        or OWNER and that the account quota for teams has
        not been exceeded.
        """
        if self.action == "create":
            try:
                account = Account.objects.get(
                    **filter_from_ident(self.kwargs["account"]),
                    users__user=self.request.user,
                    users__role__in=[AccountRole.MANAGER.name, AccountRole.OWNER.name],
                )
            except Account.DoesNotExist:
                raise exceptions.PermissionDenied

            AccountQuotas.TEAMS.check(account)

        try:
            return {
                "list": AccountTeamSerializer,
                "create": AccountTeamCreateSerializer,
                "retrieve": AccountTeamSerializer,
                "partial_update": AccountTeamUpdateSerializer,
                "destroy": AccountTeamDestroySerializer,
            }[self.action]
        except KeyError:
            raise RuntimeError("Unexpected action {}".format(self.action))

    def get_account(self, filters={}):  # noqa: D102
        try:
            return Account.objects.get(
                users__user=self.request.user,
                **filter_from_ident(self.kwargs["account"]),
                **filters,
            )
        except Account.DoesNotExist:
            raise exceptions.PermissionDenied

    def get_account_role(self):  # noqa: D102
        account = self.get_account()
        role = account.users.get(user=self.request.user).role
        return account, role

    def get_account_role_team(self):  # noqa: D102
        account, role = self.get_account_role()
        team = self.get_object(account)
        return account, role, team

    def get_queryset(self, account=None):
        """
        Get the queryset for the current action.

        For `list`, returns **all** teams for account
        after checking that the user is an account user.
        """
        if self.action == "list":
            if account is None:
                account = self.get_account()
            return AccountTeam.objects.filter(account=account)
        else:
            raise RuntimeError("Unexpected action {}".format(self.action))

    def get_object(self, account=None):
        """
        Get the object for the current action.

        For `retrieve`, checks that user is an account user.
        For `partial-update` and `destroy`, checks that the user
        is an account MANAGER or OWNER.
        """
        if self.action in ["retrieve", "partial_update", "destroy"]:
            account = self.get_account(
                {}
                if self.action == "retrieve"
                else {
                    "users__role__in": [
                        AccountRole.MANAGER.name,
                        AccountRole.OWNER.name,
                    ]
                }
            )
            return AccountTeam.objects.get(
                **filter_from_ident(self.kwargs["team"]), account=account
            )
        else:
            raise RuntimeError("Unexpected action {}".format(self.action))

    # Views

    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List teams.

        Returns a list of teams for the account.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a team.

        Returns data for the new team.
        """
        account = self.get_account()
        serializer = self.get_serializer(data=request.data)

        if self.accepts_html():
            if serializer.is_valid():
                serializer.save()
                status = self.CREATED
                headers = {
                    "Location": reverse(
                        "ui-accounts-teams-update",
                        args=[account.name, serializer.instance.name],
                    )
                }
            else:
                status = self.INVALID
                headers = {}
            return Response(
                dict(account=account, serializer=serializer),
                status=status,
                headers=headers,
            )
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=self.CREATED)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a team.

        Returns data for the team.
        """
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update a team.

        Returns data for the team.
        """
        account, role, team = self.get_account_role_team()
        serializer = self.get_serializer(team, data=request.data, partial=True)

        if self.accepts_html():
            if serializer.is_valid():
                serializer.save()
                status = self.UPDATED
                headers = {
                    "Location": reverse(
                        "ui-accounts-teams-update",
                        args=[account.name, serializer.instance.name],
                    )
                }
            else:
                status = self.INVALID
                headers = {}

            return Response(
                dict(account=account, role=role, team=team, serializer=serializer),
                status=status,
                headers=headers,
            )
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=self.UPDATED)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Destroy a team.

        Returns an empty response.
        """
        account, role, team = self.get_account_role_team()
        serializer = self.get_serializer(team, data=request.data)

        if self.accepts_html():
            if serializer.is_valid():
                team.delete()
                status = self.DESTROYED
            else:
                status = self.INVALID
            return Response(
                dict(account=account, team=team, serializer=serializer), status=status
            )
        else:
            serializer.is_valid(raise_exception=True)
            team.delete()
            return Response(status=self.DESTROYED)


class AccountsTeamsMembersViewSet(HtmxMixin, viewsets.GenericViewSet):
    """
    A view set for account team members.

    Provides views for addition (`create`) and removal (`delete`)
    of members from a team.
    """

    serializer_class = UserIdentifierSerializer

    lookup_url_kwarg = "user"

    def get_team(self):
        """
        Get the team for this request.

        Will return a 404 if the team or account does not exist
        or if the user does not have permissions to modify it.
        """
        try:
            return AccountTeam.objects.get(
                **filter_from_ident(self.kwargs["account"], prefix="account"),
                **filter_from_ident(self.kwargs["team"]),
                account__users__user=self.request.user,
                account__users__role__in=[
                    AccountRole.MANAGER.name,
                    AccountRole.OWNER.name,
                ],
            )
        except AccountTeam.DoesNotExist:
            raise exceptions.NotFound

    def get_role(self, team: AccountTeam) -> str:  # noqa: D102
        return AccountUser.objects.get(
            account=team.account, user=self.request.user
        ).role

    def get_response(self, team: AccountTeam) -> Response:
        """
        Get the response for this request.

        For HTML requests, adds the account and team to the template
        context. For JSON requests, returns an empty response.
        """
        if self.accepts_html():
            role = self.get_role(team)
            return Response(dict(account=team.account, role=role, team=team))
        else:
            return Response()

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Add a user to the team."""
        team = self.get_team()

        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        team.members.add(serializer.validated_data["user"])

        return self.get_response(team)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Remove a user from the team."""
        team = self.get_team()

        serializer = self.get_serializer(
            data=filter_from_ident(self.kwargs["user"], str_key="username")
        )
        serializer.is_valid(raise_exception=True)

        team.members.remove(serializer.validated_data["user"])

        return self.get_response(team)
