import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View

from lib.jwt import jwt_encode
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


class ManifestView(ProjectPermissionsMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        if not settings.SPARKLA_HOST:
            raise ValueError('SPARKLA_HOST setting is empty.')

        project = self.get_project(request.user, pk)

        limits = {
            'project_id': project.pk
        }

        manifest = {
            'capabilities': {
                'execute': {
                    'required': ['node'],
                    'properties': {
                        'node': {
                            'type': 'object',
                            'required': ['type', 'programmingLanguage'],
                            'properties': {
                                'type': {
                                    'enum': ['CodeChunk', 'CodeExpression']
                                },
                                'programmingLanguage': {
                                    'enum': ['python', 'r']
                                }
                            }
                        }
                    }
                }
            },
            'addresses': {
                'ws': {
                    'type': 'ws',
                    'host': settings.SPARKLA_HOST,
                    'jwt': jwt_encode(limits)
                }
            }
        }

        return JsonResponse(manifest)
