from django.db.models import QuerySet
from rest_framework import viewsets

from manager.api.helpers import (
    HtmxCreateMixin,
    HtmxDestroyMixin,
    HtmxListMixin,
    HtmxMixin,
)
from users.api.serializers import InviteSerializer
from users.models import Invite


class InvitesViewSet(
    HtmxMixin,
    HtmxListMixin,
    HtmxCreateMixin,
    HtmxDestroyMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for invites.

    Provides for `list`, `create` and `destroy` actions.
    Requires authentication because all actions are restricted
    to the `inviter` of the invite instance.
    """

    model = Invite
    serializer_class = InviteSerializer

    def get_queryset(self) -> QuerySet:
        """
        Get all invites sent by the current user.
        """
        return Invite.objects.filter(inviter=self.request.user)
