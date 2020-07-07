import datetime

from django import db
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.loader import MigrationLoader
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, serializers
from rest_framework.request import Request
from rest_framework.response import Response
from sentry_sdk import capture_message

from manager.version import __version__


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
    pagination_class = None

    @swagger_auto_schema(responses={200: StatusResponse})
    def get(self, request: Request) -> Response:
        """Get the system status."""
        try:
            pending = migrations_pending()
        except db.OperationalError as exc:
            if "could not connect to server" in str(exc):
                # A db connectivity error.
                # This can happen (but not always) during both deployment startup
                # and shutdown. So just return a 503.
                # This is OK because broader db connectivity issues will be raised
                # elsewhere in the deployed version.
                # See https://github.com/stencila/hub/issues/336
                return Response(str(exc), status=503)
            else:
                # In case this is some other sort of error re-raise it.
                raise exc

        if pending:
            # Send a message to Sentry so that maintainers are alerted of the need
            # to do migrations for this version
            message = "Migrations pending for v{}".format(__version__)
            capture_message(message, level="error")
            # Tell the requester we are not ready
            return Response(message, status=503)

        # Otherwise, just a response with a bit on info and the right headers
        response = Response(
            {"time": datetime.datetime.utcnow().isoformat(), "version": __version__}
        )
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response


def migrations_pending() -> bool:
    """
    Check if there are any migrations that haven't been applied yet.

    Inspired by https://tech.octopus.energy/news/2016/05/05/django-elb-health-checks.html
    """
    connection = connections[DEFAULT_DB_ALIAS]
    loader = MigrationLoader(connection)
    graph = loader.graph

    # Count unapplied migrations
    for app_name in loader.migrated_apps:
        for node in graph.leaf_nodes(app_name):
            for plan_node in graph.forwards_plan(node):
                if plan_node not in loader.applied_migrations:
                    return True

    return False
