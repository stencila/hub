"""
A model
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from projects.models import Project, Session


class ProjectHostBaseView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        origin = self.request.META.get('HTTP_ORIGIN')
        #referer = self.request.META.get('HTTP_REFERER')
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        return response


class ProjectHostManifestView(ProjectHostBaseView):

    def get(self, request, token):
        project = get_object_or_404(Project, token=token)

        return JsonResponse({
            'id': 'stencila-hub-project-{}'.format(project.id),
            'stencila': {
                'package': 'hub',
                'version': '0.0'
            },
            'environs': [
                {
                    'id': 'project-{}'.format(project.id),
                    'name': 'project',
                    'version': 'project'
                }
            ],
            'services': []
        })


class ProjectHostSessionsView(ProjectHostBaseView):

    def post(self, request, token, environ):
        project = get_object_or_404(Project, token=token)
        session = Session.create(project=project)

        return JsonResponse({
            'url': session.url
        })
