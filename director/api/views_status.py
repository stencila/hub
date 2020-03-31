import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, serializers, generics
from rest_framework.request import Request
from rest_framework.response import Response
from sentry_sdk import capture_message
import psycopg2

from lib.health_check import migrations_pending
from version import __version__


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
    to check the status of the instance. Returns a 50X status code if the instance is
    not healthy. Will create a Sentry message if there are database migrations pending.
    """

    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(responses={200: StatusResponse})
    def get(self, request: Request) -> Response:
        try:
            pending = migrations_pending()
        except psycopg2.OperationalError as exc:
            if "could not connect to server" in str(exc):
                # A db connectivity error.
                # This can happen (but not always) during initial deployment warmup.
                # Treat it as a migrations pending.
                # This is OK because broader db connectivity issues will be raised
                # elsewhere in the deployed version.
                # See https://github.com/stencila/hub/issues/336
                pending = True
            else:
                # In case this is some other sort of error re-raise it.
                raise exc

        if pending:
            # Send a message to Sentry so that maintainers are alerted of the need
            # to do migrations for this version
            capture_message(
                "Migrations pending for v{}".format(__version__), level="error"
            )
            # Tell the requester we are not ready
            return Response(status=503)

        # Otherwise, just a response with a bit on info and the right headers
        response = Response(
            {"time": datetime.datetime.utcnow().isoformat(), "version": __version__}
        )
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response
