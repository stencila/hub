from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from general.api.exceptions import ConflictError
from lib.data_cleaning import logged_in_or_none
from projects.models import Snapshot
from projects.project_models import ProjectEvent, ProjectEventType, ProjectEventLevel
from projects.snapshots import ProjectSnapshotter, SnapshotInProgressError
from projects.views.mixins import ProjectPermissionsMixin, ProjectPermissionType
from projects.api.serializers import SnapshotSerializer, SnapshotCreateRequestSerializer


class SnapshotsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    ProjectPermissionsMixin,
):

    serializer_class = SnapshotSerializer
    lookup_field = "number"

    def get_permissions(self):
        """
        Get the list of permissions that the current action requires.

        - `list` and `retrieve`: auth not required but access denied for private projects
        - `create`: auth required
        """
        if self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def list(self, request: Request, pk: int) -> Response:
        """
        List snapshots of the project.

        Returns a list of snapshots created for the project.
        """
        project = self.get_project(request.user, pk=pk)
        if not self.has_permission(ProjectPermissionType.VIEW):
            raise PermissionDenied

        queryset = project.snapshots.all()
        serializer = SnapshotSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SnapshotCreateRequestSerializer,
        responses={status.HTTP_201_CREATED: SnapshotSerializer},
    )
    def create(self, request: Request, pk: int) -> Response:
        """
        Create a snapshot of the project.

        Optionally, receives a `tag` for the new snapshot.
        Returns the details of the created snapshot.
        """
        serializer = SnapshotCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tag = serializer.validated_data.get("tag")

        # Check that the user has EDIT permissions for the project
        project = self.get_project(request.user, pk=pk)
        if not self.has_permission(ProjectPermissionType.EDIT):
            raise PermissionDenied

        # Create the snapshotter and event for the snapshot
        snapshotter = ProjectSnapshotter(settings.STENCILA_PROJECT_STORAGE_DIRECTORY)
        event = ProjectEvent.objects.create(
            event_type=ProjectEventType.SNAPSHOT.name,
            project=project,
            user=logged_in_or_none(request.user),
            level=ProjectEventLevel.INFORMATIONAL.value,
        )
        try:
            snapshot = snapshotter.snapshot_project(request, project, tag)
            event.success = True
            event.save()

            serializer = SnapshotSerializer(snapshot)
            return Response(serializer.data, status=status.HTTP_201_CREATED,)
        except SnapshotInProgressError:
            in_progress_message = "A snapshot is already in progress for project {}.".format(
                pk
            )
            event.success = False
            event.level = ProjectEventLevel.WARNING.value
            event.message = in_progress_message
            event.save()
            raise ConflictError(in_progress_message)
        except IntegrityError as e:
            event.level = ProjectEventLevel.ERROR.value
            event.success = False
            if tag:
                # this will usually be the thing that causes an IntegrityError
                error_message = 'A snapshot with tag "{}" already exists for project {}.'.format(
                    tag, pk
                )
            else:
                error_message = str(e)
            event.message = error_message
            event.save()
            raise ConflictError(error_message)
        except Exception as e:
            event.level = ProjectEventLevel.ERROR.value
            event.success = False
            event.message = str(e)
            event.save()
            raise
        finally:
            event.finished = timezone.now()
            event.save()

    @swagger_auto_schema(responses={status.HTTP_200_OK: SnapshotSerializer},)
    def retrieve(self, request: Request, pk: int, number: int) -> Response:
        """
        Retrieve a snapshot of the project.

        Returns details of the snapshot, including date/time `created`
        and `completed`, and any `tag`.
        """
        # Check that the user has VIEW permissions for the project
        self.get_project(request.user, pk=pk)
        if not self.has_permission(ProjectPermissionType.VIEW):
            raise PermissionDenied

        snapshot = get_object_or_404(Snapshot, project=pk, version_number=number)
        serializer = SnapshotSerializer(snapshot)
        return Response(serializer.data)
