import json
import typing

import django_filters
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.views import APIView

from lib.data_cleaning import logged_in_or_none
from lib.sparkla import generate_manifest
from projects.permission_models import ProjectPermissionType
from projects.project_data import get_projects
from projects.project_models import ProjectEvent, ProjectEventType, ProjectEventLevel
from projects.snapshots import ProjectSnapshotter, SnapshotInProgressError
from projects.views.mixins import ProjectPermissionsMixin

from projects.api.serializers import ProjectSerializer, ProjectEventSerializer


class ProjectListView(generics.ListAPIView):
    """
    Get a list of projects.

    Returns a list of project that the authenticated user has access to.
    """

    serializer_class = ProjectSerializer

    def get_queryset(self):
        fetch_result = get_projects(self.request.user, None)
        return fetch_result.projects


class ProjectEventListViewBase(generics.ListAPIView):
    swagger_schema = None
    serializer_class = ProjectEventSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['event_type']

    def get_base_queryset(self):
        raise NotImplementedError('Subclasses must implement get_base_queryset')

    def get_queryset(self):
        filtered = self.get_base_queryset()
        if 'success' in self.request.query_params:
            success = self.request.query_params['success']

            if success == 'true':
                filtered = filtered.filter(success=True)
            elif success == 'false':
                filtered = filtered.filter(success=False)
            elif success == 'null':
                filtered = filtered.filter(success__isnull=True)

        return filtered


class ProjectEventListView(ProjectEventListViewBase, ProjectPermissionsMixin):  # type: ignore # get_object override
    swagger_schema = None
    project_permission_required = ProjectPermissionType.MANAGE

    def get_base_queryset(self):
        project = self.get_project(self.request.user, pk=self.kwargs['project_pk'])
        return ProjectEvent.objects.filter(project=project)


class AdminProjectEventListView(ProjectEventListViewBase):
    swagger_schema = None
    permission_classes = [IsAdminUser]

    def get_base_queryset(self):
        return ProjectEvent.objects.all()


class ManifestView(ProjectPermissionsMixin, APIView):
    swagger_schema = None

    def get(self, request: HttpResponse, pk: int) -> HttpResponse:  # type: ignore
        return self.dispatch_response(request, pk)

    def post(self, request: HttpResponse, pk: int) -> HttpResponse:  # type: ignore
        return self.dispatch_response(request, pk)

    def dispatch_response(self, request: HttpRequest, pk: int):
        # DRF overrides `dispatch()` already so we have to use the method named methods above and call this manually
        if request.user.is_anonymous or not request.user.is_staff:
            raise PermissionDenied

        project = self.get_project(request.user, pk=pk)

        json_rpc_response = False

        if request.method == 'POST':
            json_rpc_response = True

            json_rpc = json.loads(request.body)

            if json_rpc.get('method') != 'manifest':
                raise ValueError('Request is not for manifest')

        manifest = generate_manifest('{}'.format(request.user.id), project=project)

        response: typing.Any = None

        if json_rpc_response:
            response = {
                'jsonrpc': '2.0',
                'result': manifest,
                'id': json_rpc['id']
            }
        else:
            response = manifest

        return JsonResponse(response, safe=False)


class SnapshotView(ProjectPermissionsMixin, APIView):
    swagger_schema = None
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: Request, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk=pk)

        snapshotter = ProjectSnapshotter(settings.STENCILA_PROJECT_STORAGE_DIRECTORY)
        event = ProjectEvent.objects.create(event_type=ProjectEventType.SNAPSHOT.name, project=project,
                                            user=logged_in_or_none(request.user),
                                            level=ProjectEventLevel.INFORMATIONAL.value)
        tag = request.data.get('tag')
        try:
            snapshot = snapshotter.snapshot_project(request, project, tag)
            event.success = True
            event.save()
            return JsonResponse({'success': True, 'url': reverse('snapshot_files',
                                                                 args=(
                                                                     project.account.name,
                                                                     project.name,
                                                                     snapshot.version_number)
                                                                 )
                                 })
        except SnapshotInProgressError:
            in_progress_message = 'A snapshot is already in progress for Project {}.'.format(pk)
            event.success = False
            event.level = ProjectEventLevel.WARNING.value
            event.message = in_progress_message
            event.save()
            return JsonResponse(
                {'success': False, 'error': in_progress_message})
        except IntegrityError as e:
            event.level = ProjectEventLevel.ERROR.value
            event.success = False
            if tag:
                # this will usually be the thing that causes an IntegrityError
                error_message = 'A snapshot with tag "{}" already exists for Project {}.'.format(tag, pk)
            else:
                error_message = str(e)
            event.message = error_message
            event.save()
            return JsonResponse({'success': False, 'error': error_message})
        except Exception as e:
            event.level = ProjectEventLevel.ERROR.value
            event.success = False
            event.message = str(e)
            event.save()
            raise
        finally:
            event.finished = timezone.now()
            event.save()


# These are not DRF Views but they probably should be
class ProjectDetailView(ProjectPermissionsMixin, View):
    swagger_schema = None
    project_permission_required = ProjectPermissionType.VIEW

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk=pk)

        if not self.has_permission(ProjectPermissionType.MANAGE):
            raise PermissionDenied('You do not have permission to edit this Project.')

        update_data = json.loads(request.body)

        project_updated = False

        for key, value in update_data.items():
            if not hasattr(project, key):
                raise ValueError('Invalid update data key: "{}".'.format(key))

            setattr(project, key, value)
            project_updated = True

        if project_updated:
            project.save()

        return JsonResponse(
            {'success': True}
        )
