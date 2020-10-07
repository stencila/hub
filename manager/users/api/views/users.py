from django.db.models import Q, QuerySet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from manager.api.helpers import HtmxMixin
from users.api.serializers import MeSerializer, UserSerializer
from users.models import User


class UsersViewSet(
    HtmxMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for users.

    Currently only provides `list` and `retrieve` actions.
    Authentication is only required for the `me` action.
    """

    model = User
    lookup_url_kwarg = "user"
    permission_classes = ()

    def get_queryset(self) -> QuerySet:
        """
        Get all users, or only those matching the search query (if provided).

        Often, fields from the user's personal account (e.g. image) will be wanted
        so that is `select_related`ed.
        """
        queryset = User.objects.all().select_related("personal_account")

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        limit = self.request.GET.get("limit")
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                pass
            else:
                queryset = queryset[:limit]

        return queryset

    def get_object(self) -> User:
        """
        Override of `GenericAPIView.get_object`.

        Allows use of `id` or `username` to fetch a user.
        """
        user = self.kwargs.get("user")
        try:
            try:
                return User.objects.get(id=user)
            except ValueError:
                return User.objects.get(username=user)
        except User.DoesNotExist:
            raise exceptions.NotFound

    def get_serializer_class(self):
        """
        Override of `GenericAPIView.get_serializer_class`.

        Returns different serializers for different views.
        """
        return MeSerializer if self.action == "me" else UserSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="String to search for within user usernames, first and last names and email addresses.",
                type=openapi.TYPE_STRING,
            )
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List users.

        The optional `search` parameter is a search string used to filter user.
        Returns details on each user.
        """
        queryset = self.get_queryset()

        if self.accepts_html():
            return Response(dict(queryset=queryset))
        else:
            pages = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pages, many=True)
            return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user",
                openapi.IN_PATH,
                description="Username or integer id",
                type=openapi.TYPE_STRING,
            )
        ]
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a user.

        Returns details of the user.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: MeSerializer})
    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=None,
    )
    def me(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve the current user.

        Returns details of the user who is currently authenticated.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
