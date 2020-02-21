import json
import typing

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views import View
from rest_framework import generics
from rest_framework.views import APIView

from lib.sparkla import generate_manifest
from projects.api_serializers import ProjectSerializer, ProjectEventSerializer
from projects.permission_models import ProjectPermissionType
from projects.project_data import get_projects
from projects.project_models import ProjectEvent, ProjectEventType, ProjectEventLevel
from projects.snapshots import ProjectSnapshotter, SnapshotInProgressError
from projects.views.mixins import ProjectPermissionsMixin


class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        fetch_result = get_projects(self.request.user, None)
        return fetch_result.projects


class ProjectEventListView(generics.ListAPIView, ProjectPermissionsMixin):  # type: ignore # due to get_object override
    serializer_class = ProjectEventSerializer
    project_permission_required = ProjectPermissionType.MANAGE

    def get_queryset(self):
        project = self.get_project(self.request.user, pk=self.kwargs['project_pk'])
        return ProjectEvent.objects.filter(project=project)


class ManifestView(ProjectPermissionsMixin, APIView):
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
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk=pk)

        snapshotter = ProjectSnapshotter(settings.STENCILA_PROJECT_STORAGE_DIRECTORY)
        event = ProjectEvent.objects.create(event_type=ProjectEventType.SNAPSHOT.name, project=project,
                                            user=request.user, level=ProjectEventLevel.INFORMATIONAL.value)
        try:
            snapshotter.snapshot_project(request, project, request.data.get('tag'))
            return JsonResponse({'success': True})
        except SnapshotInProgressError:
            in_progress_message = 'A snapshot is already in progress for Project {}.'.format(pk)
            event.level = ProjectEventLevel.WARNING.value
            event.message = in_progress_message
            event.save()
            return JsonResponse(
                {'success': False, 'error': in_progress_message})
        except Exception as e:
            event.level = ProjectEventLevel.ERROR.value
            event.message = str(e)
            event.save()
            raise
        finally:
            event.finished = timezone.now()
            event.save()


# These are not DRF Views but they probably should be
class ProjectDetailView(ProjectPermissionsMixin, View):
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
