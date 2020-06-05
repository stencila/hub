from django.db.models import Prefetch
from rest_framework import exceptions, mixins, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.api.serializers import (
    AccountCreateSerializer,
    AccountRetrieveSerializer,
    AccountSerializer,
    AccountUpdateSerializer,
    TeamCreateSerializer,
    TeamSerializer,
    TeamUpdateSerializer,
)
from accounts.models import Account, AccountQuotas, AccountUser, Team
from manager.api.helpers import filter_from_ident


class AccountsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
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
        the data returned is restricted according to user).
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
            AccountQuotas.ORGS.check(
                user.personal_account, Account.objects.filter(creator=user).count(),
            )

        try:
            return {
                "list": AccountSerializer,
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
        if self.action == "list":
            return Account.objects.all()
        else:
            raise RuntimeError("Unexpected action {}".format(self.action))

    def get_object(self):
        """
        Get the object for the current action.

        For `retrieve`, prefetches related data.
        For `partial-update` and `update`, checks that the user
        is an account MANAGER or ADMIN.
        """
        user = self.request.user
        ident = self.kwargs["account"]
        queryset = Account.objects.filter(**filter_from_ident(ident))
        if self.action == "retrieve":
            # The `AccountRetrieveSerializer` uses nested serializers
            # for `teams` and `users`. So we use `prefetch_related`
            # to reduce the number of DB queries
            filter = filter_from_ident(ident, prefix="account")
            queryset = queryset.prefetch_related(
                Prefetch(
                    "teams",
                    queryset=Team.objects.filter(**filter).prefetch_related("members"),
                ),
                Prefetch(
                    "users",
                    queryset=AccountUser.objects.filter(**filter).select_related(
                        "user"
                    ),
                ),
            )
        elif self.action in ["partial_update", "update"]:
            if (
                queryset.filter(
                    users__user=user, users__role__in=["MANAGER", "ADMIN"]
                ).count()
                == 0
            ):
                raise exceptions.PermissionDenied
        else:
            raise RuntimeError("Unexpected action {}".format(self.action))

        try:
            return queryset[0]
        except IndexError:
            raise exceptions.NotFound("Could not find account '{}'".format(ident))

    # Views

    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List accounts.

        Returns a list of accounts.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create an account.

        Returns data for the new account.
        """
        return super().create(request, *args, **kwargs)

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
        return super().partial_update(request, *args, **kwargs)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update an account.

        Returns data for the updated account.
        """
        return super().update(request, *args, **kwargs)


class TeamsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
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
        or ADMIN and that the account quota for teams has
        not been exceeded.
        """
        if self.action == "create":
            try:
                account = Account.objects.get(
                    **filter_from_ident(self.kwargs["account"]),
                    users__user=self.request.user,
                    users__role__in=["MANAGER", "ADMIN"]
                )
            except Account.DoesNotExist:
                raise exceptions.PermissionDenied

            AccountQuotas.TEAMS.check(
                account, Team.objects.filter(account=account).count(),
            )

        try:
            return {
                "list": TeamSerializer,
                "create": TeamCreateSerializer,
                "retrieve": TeamSerializer,
                "partial_update": TeamUpdateSerializer,
                "update": TeamUpdateSerializer,
            }[self.action]
        except KeyError:
            raise RuntimeError("Unexpected action {}".format(self.action))

    def get_queryset(self):
        """
        Get the queryset for the current action.

        For `list`, returns **all** teams for account
        after checking that the user is an account user.
        """
        if self.action == "list":
            try:
                account = Account.objects.get(
                    **filter_from_ident(self.kwargs["account"]),
                    users__user=self.request.user
                )
            except Account.DoesNotExist:
                raise exceptions.PermissionDenied

            return Team.objects.filter(account=account)
        else:
            raise RuntimeError("Unexpected action {}".format(self.action))

    def get_object(self):
        """
        Get the object for the current action.

        For `retrieve`, checks that user is an account user.
        For `partial-update` and `update`, checks that the user
        is an account MANAGER or ADMIN.
        """
        user = self.request.user
        if self.action in ["retrieve", "partial_update", "update"]:
            try:
                account = Account.objects.get(
                    **filter_from_ident(self.kwargs["account"]),
                    users__user=user,
                    **(
                        {}
                        if self.action == "retrieve"
                        else {"users__role__in": ["MANAGER", "ADMIN"]}
                    )
                )
            except Account.DoesNotExist:
                raise exceptions.PermissionDenied

            return Team.objects.get(
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
        return super().create(request, *args, **kwargs)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a team.

        Returns data for the team.
        """
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update a team.

        Returns data for the updated team.
        """
        return super().partial_update(request, *args, **kwargs)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update a team.

        Returns data for the updated team.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Destroy a team.

        Returns an empty response.
        """
        return super().destroy(request, *args, **kwargs)
