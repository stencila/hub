from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.exceptions import ParseError

from users.api.serializers import UserSerializer

User = get_user_model()

USER_QUERY_MIN_LENGTH = 3


class UserSearch(generics.ListAPIView):
    permission_classes = ()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "q",
                openapi.IN_QUERY,
                description="String to search for within user usernames, first and last names and email addresses.",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_queryset(self) -> QuerySet:
        query = self.request.query_params.get("q")
        if query is None:
            raise ParseError("Parameter `q` is required")

        return User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )
