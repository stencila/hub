from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from manager.api.helpers import HtmxListMixin
from projects.api.serializers import GithubRepoSerializer
from projects.models.providers import GithubRepo


class GithubReposViewSet(
    HtmxListMixin, viewsets.GenericViewSet,
):
    """
    A view set for Github repositories the current user is a member of.
    """

    lookup_url_kwarg = "repo"
    queryset_name = "repos"
    serializer_class = GithubRepoSerializer

    def get_queryset(self):
        """
        Get the GitHub repos for a user.
        """
        queryset = GithubRepo.objects.filter(user=self.request.user)

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(full_name__icontains=search)

        return queryset.order_by("-updated")

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="A string to search for in the repo's `full_name`.",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List GitHub repositories that the current user is a member of.

        Returns a list of GitHub repositories that the user is a member of
        (i.e. has "admin", "pull", or "push" rights) in decending order of
        last update. The returned list can be filtered using query parameter
        `search` which search in the full name (i.e. owner/name) of the repo.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["POST"])
    def refresh(self, request: Request, *args, **kwargs) -> Response:
        """
        Refresh the list of GitHub repositories for the current user.

        Returns an empty response on success.
        """
        GithubRepo.refresh_for_user(self.request.user)
        return Response()
