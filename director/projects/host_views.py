"""
Views that implement some of the Stencila Host API endpoints
for a project
"""
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from projects.cloud_session_controller import CloudClient, CloudSessionFacade
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

    def get(self, request, token, version=1):
        project = get_object_or_404(Project, token=token)

        manifest = {
            'id': 'hub-project-host-{}'.format(project.id),
            'stencila': {
                'package': 'hub',
                'version': '0.1'
            },
            'environs': [
                # TODO: this should come from the list of environments
                # available for this project.
                {
                    'id': 'stencila/core',
                    'name': 'stencila/core',
                    'version': '0.1'
                }
            ],
            'services': []
        }

        # Modifications to manifest depending upon API version
        if version == 0:
            manifest['types'] = manifest['services']
            del manifest['services']

        return JsonResponse(manifest)


class ProjectHostSessionsView(ProjectHostBaseView):
    def post(self, request, token: str, environ: str) -> JsonResponse:
        project = get_object_or_404(Project, token=token)

        # TODO: This will eventually come from the `SessionParameters` for this project
        host_url = settings.NATIVE_HOST_URL
        jwt_secret = settings.JWT_SECRET  # TODO: This will eventually come from the settings for the remote host

        cloud_client = CloudClient(host_url, jwt_secret)

        session_facade = CloudSessionFacade(project, cloud_client)

        session = session_facade.create_session(environ)

        return JsonResponse({
            'url': session.url
        })
