from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from projects.api.serializers import ProjectEventSerializer
from projects.permission_models import ProjectPermissionType
from projects.project_models import ProjectEvent
from projects.views.mixins import ProjectPermissionsMixin


class EventListView(generics.ListAPIView, ProjectPermissionsMixin):
    serializer_class = ProjectEventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["event_type"]
    project_permission_required = ProjectPermissionType.MANAGE

    def get_queryset(self):
        project = self.get_project(self.request.user, pk=self.kwargs["pk"])

        filtered = ProjectEvent.objects.filter(project=project)

        if "success" in self.request.query_params:
            success = self.request.query_params["success"]

            if success == "true":
                filtered = filtered.filter(success=True)
            elif success == "false":
                filtered = filtered.filter(success=False)
            elif success == "null":
                filtered = filtered.filter(success__isnull=True)

        return filtered
