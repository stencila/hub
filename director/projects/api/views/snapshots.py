import os

from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    negotiation,
    mixins,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from general.api.exceptions import ConflictError
from lib.converter_facade import (
    ConverterFacade,
    ConverterIo,
    ConverterIoType,
    ConverterContext,
)
from lib.conversion_types import ConversionFormatId
from lib.data_cleaning import logged_in_or_none
from projects.models import Snapshot
from projects.project_models import ProjectEvent, ProjectEventType, ProjectEventLevel
from projects.snapshots import ProjectSnapshotter, SnapshotInProgressError
from projects.views.mixins import ProjectPermissionsMixin, ProjectPermissionType
from projects.api.serializers import SnapshotSerializer, SnapshotCreateRequestSerializer
from projects.source_operations import snapshot_path


class SnapshotsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    ProjectPermissionsMixin,
):

    # Settings

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

    def get_content_negotiator(self):
        """
        Customise the content negotiator for the `retrieve_file` action.

        This avoids DRF raising a not NotAcceptable exception for that
        action. Instead, the action handles content negotiation itself.
        """
        if self.name == "Retrieve file":
            return IgnoreClientContentNegotiation()
        else:
            return super().get_content_negotiator()

    # Views

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

    @action(detail=True, methods=["get"], url_path="(?P<path>.+)")
    def retrieve_file(
        self, request: Request, pk: int, number: int, path: str
    ) -> Response:
        """
        Retrieve a file within the snapshot of the project.

        Returns the content of the file, either as is, or converted
        to the desired format as specified in the `format` query parameter
        or the `Accept` header.
        """
        # Check that the user has VIEW permissions for the project
        project = self.get_project(request.user, pk=pk)
        if not self.has_permission(ProjectPermissionType.VIEW):
            raise PermissionDenied

        snapshot = get_object_or_404(Snapshot, project=pk, version_number=number)

        file_path = snapshot_path(snapshot, path)
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            raise NotFound

        # Determine the desired format
        format = request.query_params.get("format")
        if format is not None:
            format_id = ConversionFormatId.from_id(format)
        else:
            accept = request.META.get("HTTP_ACCEPT")
            if accept is not None and accept != "*/*":
                media_types = [token.strip() for token in accept.split(",")]
                format_id = ConversionFormatId.from_mimetype(media_types[0])
            else:
                format_id = None

        raw = request.query_params.get("raw")
        if raw or format_id is None:
            # Respond with the file
            response_path = file_path
        else:
            # Generate file for the format if necessary and return it
            response_path = snapshot_path(
                snapshot, ".cache/{}.{}".format(path, format_id.value.default_extension)
            )
            if not os.path.exists(response_path):
                ConverterFacade(settings.STENCILA_BINARY).convert(
                    input_data=ConverterIo(ConverterIoType.PATH, file_path),
                    output_data=ConverterIo(ConverterIoType.PATH, response_path),
                    context=ConverterContext(standalone=True),
                )
        file = open(response_path, "rb")

        # Return "binary" files as attachments
        if format_id is None or format_id.value.is_binary:
            return FileResponse(file, as_attachment=True)

        # Return other files as plain HTTP responses
        # with `Content-Type` set appropriately and allowing for them to
        # be used as <iframe> sources
        response = HttpResponse(file.read(), content_type=format_id.value.mimetypes[0])

        # Add headers if the account has a `hosts` setting
        hosts = settings.ACCOUNT_HOSTS.get(project.account.name, None)
        if hosts:
            # CSP `frame-ancestors` for modern browers
            response["Content-Security-Policy"] = "frame-ancestors {};".format(hosts)
            # `X-Frame-Options` for older browsers (only allows one value)
            host = hosts.split()[0]
            response["X-Frame-Options"] = "allow-from {}".format(host)

        return response


class IgnoreClientContentNegotiation(negotiation.BaseContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix):
        """
        Select a renderer for the `retrieve_file` action.

        This returns the first default renderer (usually JSON),
        to be for any exceptions. The action itself handles normal
        content negotiation and rendering.
        """
        return (renderers[0], renderers[0].media_type)
