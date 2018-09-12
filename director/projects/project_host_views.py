"""
Views that implement some of the Stencila Host API endpoints
for a project
"""
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from projects.cloud_session_controller import CloudClient, CloudSessionFacade
from projects.models import Project
from projects.session_models import Session

SESSION_URL_SESSION_KEY_FORMAT = 'CLOUD_SESSION_URL_{}_{}'


class ProjectHostBaseView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        origin = self.request.META.get('HTTP_ORIGIN')
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

        if project.key and request.POST.get("key") != project.key:
            raise PermissionDenied("The key in the POST request does not match that of the Project")

        session_key = SESSION_URL_SESSION_KEY_FORMAT.format(token, environ)

        # TODO: This will eventually come from the `SessionParameters` for this project
        host_url = settings.NATIVE_HOST_URL
        jwt_secret = settings.JWT_SECRET  # TODO: This will eventually come from the settings for the remote host

        cloud_client = CloudClient(host_url, jwt_secret)

        session_facade = CloudSessionFacade(project, cloud_client)

        session_url = None

        if session_key in request.session:
            session_url = request.session[session_key]
            try:
                session = Session.objects.get(url=session_url)
            except Session.DoesNotExist:
                session_url = None
            else:
                if session.stopped is None:
                    session_facade.update_session_info(session)

                if session.stopped is not None and session.stopped <= timezone.now():
                    session_url = None

        if not session_url:
            session = session_facade.create_session(environ)
            session_url = session.url
            request.session[session_key] = session_url

        return JsonResponse({
            'url': session_url
        })
