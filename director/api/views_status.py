import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, serializers, generics
from rest_framework.request import Request
from rest_framework.response import Response
from sentry_sdk import capture_message

from lib.health_check import migrations_pending
import version


class StatusResponse(serializers.Serializer):
    """Documents the response data for the StatusView."""

    time = serializers.CharField(help_text="The current time in ISO format")

    version = serializers.CharField(help_text="The current version")

    class Meta:
        ref_name = None


class StatusView(generics.GenericAPIView):
    """
    Get the current system status.

    Primarily intended as an endpoint for load balancers and other network infrastructure
    to check the status of the instance. Returns a 50X status code if the instance is not healthy.
    """

    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(responses={200: StatusResponse})
    def get(self, request: Request) -> Response:
        # Raise an exception so that maintainers are alerted of the need to do migrations
        if migrations_pending():
            capture_message("Migrations pending!", level="error")
            return Response(status=503)

        response = Response(
            {
                "time": datetime.datetime.utcnow().isoformat(),
                "version": version.__version__,
            }
        )
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response
