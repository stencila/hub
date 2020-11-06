from django.db import connection
from rest_framework import exceptions, generics
from rest_framework.request import Request
from rest_framework.response import Response

from manager.api.helpers import HtmxMixin
from users.models import Flag


class FeaturesView(
    HtmxMixin, generics.GenericAPIView,
):
    """
    A view for getting and setting user feature flags.

    This is not a `ViewSet` because it involves a non-standard
    approach to both getting and setting of feature flags.
    """

    def get_features(self, request):
        """
        Get a dictionary of feature settings for the current user.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT "name", "default", "user_id"
                FROM users_flag
                LEFT JOIN (
                    SELECT *
                    FROM users_flag_users
                    WHERE user_id = %s
                ) ON users_flag.id = flag_id
                WHERE users_flag.settable
                """,
                [request.user.id],
            )
            rows = cursor.fetchall()

        features = {}
        for row in rows:
            name, default, has_flag = row
            if has_flag:
                features[name] = "off" if default == "on" else "on"
            else:
                features[name] = default

        return features

    def get(self, request: Request) -> Response:
        """
        Get the feature settings for the current user.
        """
        features = self.get_features(request)
        return Response(features)

    def patch(self, request: Request) -> Response:
        """
        Update the feature settings for the current user.
        """
        flags = Flag.objects.filter(settable=True)

        features = request.data
        for name, value in features.items():
            try:
                flag = flags.get(name=name)
            except Flag.DoesNotExist:
                raise exceptions.ValidationError(
                    dict(feature='Invalid feature name "{0}"'.format(name))
                )

            if value not in (True, False, "on", "off"):
                raise exceptions.ValidationError(
                    dict(state='Invalid feature state "{0}"'.format(value))
                )
            if value is True:
                value = "on"
            elif value is False:
                value = "off"

            if value != flag.default:
                flag.users.add(request.user)
            else:
                flag.users.remove(request.user)

        if self.accepts_html():
            return Response(dict(flags=flags))
        else:
            features = self.get_features(request)
            return Response(features)
