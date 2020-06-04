import logging
import re

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.api.serializers import AccountCreateUpdateSerializer, AccountSerializer
from accounts.models import Account

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

    # Configuration

    def get_queryset(self):
        """
        Override of `GenericAPIView.get_queryset`.

        Returns the accounts that the user has at least `view`
        permissions for.
        """
        return Account.objects.all()  # TODO

    def get_object(self):
        """
        Override of `GenericAPIView.get_object`.

        Allow for the `id` URL kwarg to be either an integer `pk`
        or a string `name`.
        """
        id = self.kwargs["id"]
        filter_kwargs = dict(pk=int(id)) if re.match(r"\d+", id) else dict(name=id)
        obj = get_object_or_404(Account, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

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
