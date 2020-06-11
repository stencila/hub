from django.db.models import Prefetch, Q
from django.db.models.expressions import RawSQL
from django.shortcuts import reverse
from django.utils.http import urlencode
from rest_framework import exceptions, mixins, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.api.serializers import (
    AccountCreateSerializer,
    AccountListSerializer,
    AccountRetrieveSerializer,
    AccountSerializer,
    AccountTeamCreateSerializer,
    AccountTeamDestroySerializer,
    AccountTeamSerializer,
    AccountTeamUpdateSerializer,
    AccountUpdateSerializer,
    AccountUserCreateSerializer,
    AccountUserSerializer,
)
from accounts.models.account import Account, AccountRole, AccountTeam, AccountUser
from accounts.models.quota import AccountQuotas
from manager.api.helpers import HtmxMixin, filter_from_ident
from users.api.serializers import UserIdentifierSerializer


class AccountsViewSet(
    HtmxMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):
    """
    A view set for accounts.

    Provides basic account CRU(D) views.
    """

    # Configuration

    lookup_url_kwarg = "account"

    def get_permissions(self):
        """
        Get the permissions that the current action requires.

        Actions `list` and `retrive` do not require authentication (although
        the data returned is restricted).
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.

        For `create`, checks that the user has not exceeded the number
        of accounts that they can create. This is primarily an anti-spamming
        check.

        For `retrieve`, returns a detailed serializer if the user is
        a member of the account.
        #TODO: The above
        """
        if self.action == "create":
            user = self.request.user
            AccountQuotas.ORGS.check(user.personal_account)

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
        else:
            queryset = queryset.filter(user__isnull=True)

        # TODO: Find a better way to order role so MANAGER is before MEMBER
        return queryset.order_by("-role")

    def get_object(self):
        """
        Get the object for the current action.

        For `retrieve`, prefetches related data.
        For `partial-update` and `update`, checks that the user
        is an account MANAGER or OWNER.
        """
        user = self.request.user
        ident = self.kwargs["account"]

        if self.action in ["retrieve", "partial_update", "update"]:
            # The API `AccountRetrieveSerializer` uses nested serializers
            # for `teams` and `users`. Also, the UI `update` view uses the
            # number of teams and users in the side bar.
            # So we use `prefetch_related` in all cases
            # to reduce the number of DB queries
            queryset = Account.objects.filter(**filter_from_ident(ident))
            account_filter = filter_from_ident(ident, prefix="account")
            queryset = queryset.prefetch_related(
                Prefetch(
                    "teams",
                    queryset=AccountTeam.objects.filter(
                        **account_filter
                    ).prefetch_related("members"),
                ),
                Prefetch(
                    "users",
                    queryset=AccountUser.objects.filter(
                        **account_filter
                    ).select_related("user"),
                ),
            )
        else:
            raise RuntimeError("Unexpected action {}".format(self.action))

        if self.action in ["partial_update", "update"]:
            if (
                queryset.filter(
                    users__user=user,
                    users__role__in=[AccountRole.MANAGER.name, AccountRole.OWNER.name],
                ).count()
                == 0
            ):
                raise exceptions.PermissionDenied

        try:
            return queryset[0]
        except IndexError:
            raise exceptions.NotFound("Could not find account '{}'".format(ident))

    def get_account_role(self):
        """
        Get the account and the account role for the current user.

        Used in UI views to determine whether to render elements or not.
        """
        account = self.get_object()
        role = None
        if self.request.user.is_authenticated:
            try:
                role = account.users.get(user=self.request.user).role
            except AccountUser.DoesNotExist:
                pass
        return account, role

    # Views

    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List accounts.

        Returns a list of accounts.
        """
        queryset = self.get_queryset()

        if self.accepts_html():
            url = "?" + "&".join(
                [
                    "{}={}".format(key, value)
                    for key, value in self.request.GET.items()
                    if key != "is" and value
                ]
            )
            return Response(dict(accounts=queryset), headers={"X-HX-Push": url})
        else:
            pages = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pages, many=True)
            return self.get_paginated_response(serializer.data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create an account.

        Returns data for the new account.
        """
        serializer = self.get_serializer(data=request.data)

        if self.accepts_html():
            if serializer.is_valid():
                serializer.save()
                status = self.CREATED
                headers = {
                    "Location": reverse(
                        "ui-accounts-update", args=[serializer.instance.name],
                    )
                }
            else:
                status = self.INVALID
                headers = {}

            return Response(dict(serializer=serializer), status=status, headers=headers)
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=self.CREATED)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve an account.

        Returns detailed data for the account.
        """
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update an account.

        Returns data for the updated account.
        """
        account = self.get_object()
        serializer = self.get_serializer(account, data=request.data, partial=True)

        if self.accepts_html():
            if serializer.is_valid():
                serializer.save()
                status = self.UPDATED
                headers = {
                    "Location": reverse(
                        "ui-accounts-update", args=[serializer.instance.name],
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
            return Response(serializer.data, status=self.UPDATED)


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

    def get_account(self):
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

    def get_account_role(self):
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

    def get_serializer_class(self):
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

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
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

        if self.accepts_html():
            account_user.delete()
            status = self.DESTROYED  # TODO: Can't use DESTROYED because HTMX ignores it
            return Response(dict(account=account, role=role), status=200)
        else:
            account_user.delete()
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

    def get_account(self, filters={}):
        try:
            return Account.objects.get(
                users__user=self.request.user,
                **filter_from_ident(self.kwargs["account"]),
                **filters,
            )
        except Account.DoesNotExist:
            raise exceptions.PermissionDenied

    def get_account_role(self):
        account = self.get_account()
        role = account.users.get(user=self.request.user).role
        return account, role

    def get_account_role_team(self):
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

    def get_role(self, team: AccountTeam) -> str:
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
