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
    HtmxMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    A view set for projects.

    Provides basic account CRUD views.
    """

    # Configuration

    lookup_url_kwarg = "project"

    queryset = Project.objects.all()

    serializer_class = ProjectSerializer

    def get_object(self):
        return Project.objects.get(
            **filter_from_ident(self.kwargs["account"], prefix="account"),
            **filter_from_ident(self.kwargs["project"])
        )

    def get_project_role(self):
        # TODO: Get role
        return self.get_object(), ProjectRole.OWNER.name
