from django.db.models import Q
from django.shortcuts import reverse
from rest_framework import exceptions, mixins, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from manager.api.helpers import HtmxMixin, filter_from_ident
from projects.models import Project, ProjectRole

from projects.api.serializers import (  # ProjectCreateSerializer,; ProjectRetrieveSerializer,; ProjectUpdateSerializer,
    ProjectSerializer,
)


class ProjectsViewSet(
    HtmxMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):
    """
    A view set for projects.

    Provides basic account CRUD views.
    """

    # Configuration

    lookup_url_kwarg = "project"

    serializer_class = ProjectSerializer

    def get_queryset(self):
        """Get the set of projects matching the query."""
        queryset = Project.objects.all()

        account = self.request.GET.get("account")
        if account:
            queryset = queryset.filter(account_id=account)

        public = self.request.GET.get("public")
        if public:
            queryset = queryset.filter(public=public == "true")

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset

    def get_object(self):
        return Project.objects.get(
            **filter_from_ident(self.kwargs["account"], prefix="account"),
            **filter_from_ident(self.kwargs["project"])
        )

    def get_project_role(self):
        # TODO: Get role
        return self.get_object(), ProjectRole.OWNER.name

    # Views

    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List accounts.

        Returns a list of accounts.
        """
        queryset = self.get_queryset()

        if self.accepts_html():
            url = "?" + "&".join(
                [
                    "{}={}".format(key, value)
                    for key, value in self.request.GET.items()
                    if value
                ]
            )
            return Response(dict(projects=queryset), headers={"X-HX-Push": url})
        else:
            pages = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pages, many=True)
            return self.get_paginated_response(serializer.data)
