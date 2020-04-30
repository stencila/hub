import os

from django.conf import settings
from django.db import IntegrityError
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework import (
    mixins,
    permissions,
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotAcceptable, NotFound
from rest_framework.request import Request
from rest_framework.response import Response
import mimetypes
import shutil

from general.api.exceptions import ConflictError
from general.api.negotiation import IgnoreClientContentNegotiation
from lib.converter_facade import (
    ConverterFacade,
    ConverterIo,
    ConverterIoType,
    ConverterContext,
)
from lib.conversion_types import (
    conversion_format_from_id,
    conversion_format_from_mimetype,
    UnknownFormatError,
    UnknownMimeTypeError,
)
from lib.data_cleaning import logged_in_or_none
from lib.path_operations import utf8_path_join
from projects.models import Snapshot
from projects.project_models import ProjectEvent, ProjectEventType, ProjectEventLevel
from projects.snapshots import ProjectSnapshotter, SnapshotInProgressError
from projects.views.mixins import ProjectPermissionsMixin, ProjectPermissionType
from projects.api.serializers import SnapshotSerializer
from projects.source_operations import snapshot_path

# Create a dictionary of extension names (without dot) to archive formats
# Use `get_unpack_formats` instead of `get_archive_formats` because it
# provides file extension names
archive_formats = dict(
    [(format[1][0][1:], format[0]) for format in shutil.get_unpack_formats()]
)
retreive_formats = ["json"] + list(archive_formats.keys())


class SnapshotCreateRequestSerializer(serializers.ModelSerializer):
    """The request data when creating a snapshot."""

    class Meta:
        model = Snapshot
        fields = ["tag"]
        ref_name = None


class SnapshotRetrieveSchema(SwaggerAutoSchema):
    """Custom schema inspector for the retreive action."""

    def get_produces(self):
        produces = []
        for ext in retreive_formats:
            type, encoding = mimetypes.guess_type("file." + ext)
            value = "{}+{}".format(type, encoding) if encoding is not None else type
            produces.append(value)
        return produces


class SnapshotsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    ProjectPermissionsMixin,
):

    # Configuration

    queryset = Snapshot.objects.all()
    content_negotiation_class = IgnoreClientContentNegotiation
    serializer_class = SnapshotSerializer
    lookup_field = "number"

    def get_permissions(self):
        """
        Get the list of permissions that the current action requires.

        - `list` and `retrieve`: auth not required but access denied for private projects
        - `create`: auth required
        """
        return [permissions.IsAuthenticated()] if self.action == "create" else []

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
        serializer = self.get_serializer(queryset, many=True)
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
        snapshotter = ProjectSnapshotter(settings.STORAGE_DIR)
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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

    @swagger_auto_schema(auto_schema=SnapshotRetrieveSchema)
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

        # Get the request format
        format = request.query_params.get("format")
        if format is None:
            accept = request.META.get("HTTP_ACCEPT")
            if accept:
                ext = mimetypes.guess_extension(accept)
                if ext:
                    format = ext[1:]
                else:
                    format = {
                        "application/x-tar+bzip2": "tar.bz2",
                        "application/x-tar+gzip": "tar.gz",
                        "application/x-tar+xz": "tar.xz",
                    }.get(accept)

        if format is None:
            format = "json"

        if format not in retreive_formats:
            raise NotAcceptable(
                "Could not satisfy the requested format '{}', must be one of {}".format(
                    format, retreive_formats
                )
            )

        snapshot = get_object_or_404(Snapshot, project=pk, version_number=number)
        if format == "json":
            # Just return the snapshot details
            serializer = self.get_serializer(snapshot)
            return Response(serializer.data)
        else:
            # Return an archive of the snapshot using the cache if available
            archive_path = snapshot.path + "." + format
            if not os.path.exists(archive_path):
                filename = shutil.make_archive(
                    snapshot.path, archive_formats[format], snapshot.path
                )
                assert filename == archive_path
            return FileResponse(open(archive_path, "rb"), as_attachment=True)

    @action(detail=True, methods=["get"], url_path="(?P<path>.+)")
    def retrieve_file(
        self, request: Request, pk: int, number: int, path: str
    ) -> Response:
        """
        Retrieve a file within a snapshot of the project.

        Returns the content of the file, either as is (if the `raw` parameter
        is supplied), or converted to the desired format as specified in the `format`
        query parameter or the `Accept` header. Use the `download` parameter to
        force `Content-Disposition: attachment`.
        """
        # Check that the user has VIEW permissions for the project
        project = self.get_project(request.user, pk=pk)
        if not self.has_permission(ProjectPermissionType.VIEW):
            raise PermissionDenied

        snapshot = get_object_or_404(Snapshot, project=pk, version_number=number)

        file_path = snapshot_path(snapshot, path)
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            raise NotFound

        # Determine the desired format, raising a `NotAcceptable` exception
        # if the format is not supported
        try:
            format = request.query_params.get("format")
            if format is not None:
                format_id = conversion_format_from_id(format)
            else:
                accept = request.META.get("HTTP_ACCEPT")
                if accept is not None and accept != "*/*":
                    media_types = [token.strip() for token in accept.split(",")]
                    format_id = conversion_format_from_mimetype(media_types[0])
                else:
                    format_id = None
        except (UnknownFormatError, UnknownMimeTypeError):
            raise NotAcceptable(
                "Could not satisfy the request format parameter or Accept header"
            )

        # Determine the theme, defaulting to None (i.e. use Encoda's default)
        theme = (
            request.query_params.get("theme") or project.theme or project.account.theme
        )

        raw = "raw" in request.query_params
        if raw or format_id is None:
            # Respond with the file
            response_path = file_path
        else:
            # Generate file for the format if necessary and return it
            response_path = utf8_path_join(
                snapshot.path + ".cache",
                "{}{}.{}".format(
                    slugify(path.replace(".", "-")),
                    "-" + slugify(theme) if theme else "",
                    format_id.value.default_extension,
                ),
            )
            if not os.path.exists(response_path):
                ConverterFacade(settings.STENCILA_ENCODA_PATH).convert(
                    input_data=ConverterIo(ConverterIoType.PATH, file_path),
                    output_data=ConverterIo(ConverterIoType.PATH, response_path),
                    context=ConverterContext(standalone=True, theme=theme),
                )
        file = open(response_path, "rb")

        # Return "binary" files as attachments with mimetype is determined automatically from
        # the files extension.
        download = "download" in request.query_params
        if format_id is None or format_id.value.is_binary:
            as_attachment = True
            content_type = None
        else:
            as_attachment = download
            content_type = format_id.value.mimetypes[0]

        response = FileResponse(
            file, content_type=content_type, as_attachment=as_attachment
        )

        # Add headers if the account has `hosts` set
        hosts = project.account.hosts
        if hosts:
            # CSP `frame-ancestors` for modern browers
            response["Content-Security-Policy"] = "frame-ancestors {};".format(hosts)
            # `X-Frame-Options` for older browsers (only allows one value)
            host = hosts.split()[0]
            response["X-Frame-Options"] = "allow-from {}".format(host)

        return response
