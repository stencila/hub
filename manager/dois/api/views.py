from rest_framework import permissions, throttling, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from dois.api.serializers import DoiSerializer
from dois.models import Doi
from manager.api.helpers import HtmxCreateMixin, HtmxListMixin, HtmxRetrieveMixin


class DoiCreateThrottle(throttling.UserRateThrottle):
    """
    Throttle number of DOIs created per day.

    Althou account quotas for DOIs should be in place, this
    provides a further backup that things don't go haywire.
    """

    rate = "100/day"


class DoisViewSet(
    HtmxListMixin, HtmxCreateMixin, HtmxRetrieveMixin, viewsets.GenericViewSet,
):
    """
    A view set for DOIs.

    Provides basic CR(UD) views for DOIs.
    """

    lookup_url_kwarg = "doi"
    object_name = "doi"
    queryset_name = "dois"

    queryset = Doi.objects.all()
    serializer_class = DoiSerializer

    def get_permissions(self):
        """
        Get the list of permissions that the current action requires.

        The action `create` (i.e. POST) requires authentication to prevent unauthenticated
        users from creating DOIs. The `list` and `retrieve` actions do not require authentication.
        """
        return [permissions.IsAuthenticated()] if self.action == "create" else []

    def get_throttles(self):
        """
        Get the throttles to apply to the current request.
        """
        return (
            [DoiCreateThrottle()]
            if self.action == "create"
            else super().get_throttles()
        )

    # Most of the following views serve simply to provide docstrings
    # from which API documentation is generated.

    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List DOIs.

        Returns a paginated list of all DOIs.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a DOI.

        Receives details of the DOI to create and dispatches a job
        to register it.
        Returns details of the new DOI.
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a DOI.

        Returns details of the DOI.
        """
        return super().retrieve(request, *args, **kwargs)
