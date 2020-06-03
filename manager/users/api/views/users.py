from django.db.models import Q, QuerySet
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from users.api.serializers import MeSerializer, UserSerializer
from users.models import User


class UsersViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):
    """
    A view set for users.

    Currently only provides `list` and `retrieve` actions.
    Authentication is only required for the `me` action.
    """

    # Configuration

    model = User
    permission_classes = ()

    def get_queryset(self) -> QuerySet:
        """Get all users, or only those matching the search query (if provided)."""
        query = self.request.query_params.get("search")
        if query is None:
            return User.objects.all()

        return User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )

    def get_serializer_class(self):
        """
        Override of `GenericAPIView.get_serializer_class`.

        Returns different serializers for different views.
        """
        return MeSerializer if self.action == "me" else UserSerializer

    # Views

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

        The optional `q` parameter is a search string used to filter user.
        Returns details on each user.
        """
        queryset = self.get_queryset()

        template = request.query_params.get("html")
        if template is not None:
            return render(
                request,
                template or "users/_search_result.html",
                dict(queryset=queryset),
            )
        else:
            pages = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pages, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a user.

        Returns details of the user.
        """
        # This method exists only to add the above docs to the schema.
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
