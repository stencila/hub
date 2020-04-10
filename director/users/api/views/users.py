from django.db.models import QuerySet, Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from users.models import User
from users.api.serializers import UserSerializer


class UsersViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):

    # Configuration

    model = User
    permission_classes = ()
    serializer_class = UserSerializer

    def get_queryset(self) -> QuerySet:
        """Get all Users, or only those matching the query (if provided)."""
        query = self.request.query_params.get("q")
        if query is None:
            return User.objects.all()

        return User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )

    # Views

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
    def list(self, *args, **kwargs):
        """
        List users.

        The optional `q` parameter is a search string used to filter user.
        Returns details on each user.
        """
        return super().list(*args, **kwargs)

    def retrieve(self, *args, **kwargs):
        """
        Retrieve a user.

        Returns details of the user.
        """
        return super().retrieve(*args, **kwargs)

    @swagger_auto_schema(responses={200: UserSerializer})
    @action(
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=None,
    )
    def retrieve_me(self, request, *args, **kwargs):
        """
        Retrieve the current user.

        Returns details of the user who is currently authenticated.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
