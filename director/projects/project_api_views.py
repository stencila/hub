import json

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from lib.sparkla import generate_manifest
from projects.permission_models import ProjectPermissionType
from projects.project_views import ProjectPermissionsMixin


class ProjectDetailView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk)

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


@method_decorator(csrf_exempt, name='dispatch')
class ManifestView(ProjectPermissionsMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        if request.user.is_anonymous or not request.user.is_staff:
            raise PermissionDenied

        project = self.get_project(request.user, pk)

        json_rpc = json.loads(request.body)

        if json_rpc.get('method') != 'manifest':
            raise ValueError('Request is not for manifest')

        manifest = generate_manifest('{}'.format(request.user.id), project=project)

        response = {
            'jsonrpc': '2.0',
            'result': manifest,
            'id': json_rpc['id']
        }

        return JsonResponse(response)
