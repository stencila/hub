import logging

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.api.serializers import (
    AccountCreateUpdateSerializer,
    AccountSerializer,
    TeamCreateSerializer,
    TeamSerializer,
    TeamUpdateSerializer,
)
from accounts.models import Account, Team
from manager.api.helpers import get_filter_from_ident, get_object_from_ident

logger = logging.getLogger(__name__)


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

    lookup_url_kwarg = "account"

    # Configuration

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the accounts that the user has at least `view`
        permissions for.
        """
        # TODO: Filter for accounts the user has access to
        return Account.objects.all()

    def get_object(self):
        """
        Override of `GenericAPIView.get_object`.

        Allow for the `id` URL kwarg to be either an integer `pk`
        or a string `name`.
        """
        account = get_object_from_ident(Account, self.kwargs["account"])
        # TODO: check user has permissions for action on account
        return account

    def get_serializer_class(self):
        """
        Override of `GenericAPIView.get_serializer_class`.

        Returns different serializers for different views.
        """
        try:
            return {
                "list": AccountSerializer,
                "create": AccountCreateUpdateSerializer,
                "retrieve": AccountSerializer,
                "update": AccountCreateUpdateSerializer,
            }[self.action]
        except KeyError:
            logger.error("No serializer defined for action {}".format(self.action))
            return AccountSerializer

    # Views

    def list(self, request: Request) -> Response:
        """
        List accounts.

        Returns a list of accounts the user has at least `view`
        access to.
        """
        return super().list(request)

    def create(self, request: Request) -> Response:
        """
        Create an account.

        Returns details for the new account.
        """
        serializer = self.get_serializer(request.data)
        return Response(serializer.data)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve an account.

        Returns details for the account.
        """
        account = self.get_object()
        serializer = self.get_serializer(account)
        return Response(serializer.data)


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

    lookup_field = "team"

    # Configuration

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns all the teams for the account.
        """
        account = get_object_from_ident(Account, self.kwargs["account"])
        # TODO: check user has view permissions for account
        return Team.objects.filter(account=account)

    def get_object(self):
        """
        Override of `GenericAPIView.get_object`.

        Allow for the `account` and `team` URL kwargs to be either an
        integer `id` or a string `name`.
        """
        account = get_object_from_ident(Account, self.kwargs["account"])
        # TODO: check user has permissions for action on account
        return get_object_or_404(
            Team, account=account, **get_filter_from_ident(self.kwargs["team"])
        )

    def get_serializer_class(self):
        """
        Override of `GenericAPIView.get_serializer_class`.

        Returns different serializers for different views.
        """
        try:
            return {
                "list": TeamSerializer,
                "create": TeamCreateSerializer,
                "retrieve": TeamSerializer,
                "update": TeamUpdateSerializer,
            }[self.action]
        except KeyError:
            logger.error("No serializer defined for action {}".format(self.action))
            return TeamSerializer

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

        Returns details for the new team.
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a team.

        Returns details for the team.
        """
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update a team.

        Returns updated details for the team.
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Destroy a team.

        Returns an empty response.
        """
        return super().destroy(request, *args, **kwargs)
