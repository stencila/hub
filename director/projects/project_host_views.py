"""
Views that implement some of the Stencila Host API endpoints
for a project
"""
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from projects.cloud_session_controller import CloudClient, CloudSessionFacade, ActiveSessionsExceededException
from projects.models import Project
from projects.session_models import Session, SessionRequest

SESSION_URL_SESSION_KEY_FORMAT = 'CLOUD_SESSION_URL_{}_{}'
SESSION_REQUEST_SESSION_KEY_FORMAT = 'SESSION_REQUEST_ID_{}'
SESSION_REQUEST_IS_NEXT_KEY_FORMAT = 'SESSION_REQUEST_NEXT_{}'


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


class ProjectSessionRequestView(View):
    api_version: int = 0

    def get(self, request: HttpRequest, token: str) -> HttpResponse:
        project = get_object_or_404(Project, token=token)

        session_request_key = SESSION_REQUEST_SESSION_KEY_FORMAT.format(token)

        if session_request_key not in request.session:
            return HttpResponseBadRequest("No session is currently queued for you for this project token.")

        session_request_pk = request.session[session_request_key]

        try:
            session_request = SessionRequest.objects.get(pk=session_request_pk)
        except SessionRequest.DoesNotExist:
            del request.session[session_request_key]
            return JsonResponse({'invalid_session': True})  # TODO: work out what a sensible response is
            # client should stop checking if they receive this

        host_url = settings.NATIVE_HOST_URL
        jwt_secret = settings.JWT_SECRET  # TODO: This will eventually come from the settings for the remote host

        cloud_client = CloudClient(host_url, jwt_secret)

        session_facade = CloudSessionFacade(project, cloud_client)

        if project.sessions_concurrent is not None and \
                project.sessions_concurrent <= session_facade.get_active_session_count():
            # still too many running sessions
            return JsonResponse({'waiting': True})  # TODO: work out what a sensible response is

        # there are available session spots, but is this request first in the queue?
        first_session_request = SessionRequest.objects.filter(project=project).order_by('created').first()

        if first_session_request == session_request:
            request.session[SESSION_REQUEST_IS_NEXT_KEY_FORMAT.format(token)] = True  # semaphore to shortcut checks
            return JsonResponse({'start_session': True})  # TODO: work out what a sensible response is
            # client should attempt the POST again and we let them through

        return JsonResponse({'start_session': False})


class ProjectHostSessionsView(ProjectHostBaseView):
    api_version: int = 0

    def post(self, request: HttpRequest, token: str, environ: str) -> JsonResponse:
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
            is_next_key = SESSION_REQUEST_IS_NEXT_KEY_FORMAT.format(token)

            if is_next_key in request.session and request.session[is_next_key]:
                session_request_key = SESSION_REQUEST_SESSION_KEY_FORMAT.format(token)
                session_request_to_use = SessionRequest.objects.get(pk=request.session[session_request_key])
                del request.session[is_next_key]
                del request.session[session_request_key]
            else:
                session_request_to_use = None

            try:
                session = session_facade.create_session(environ, session_request_to_use)
            except ActiveSessionsExceededException:
                session_request = session_facade.create_session_request(environ)
                request.session[SESSION_REQUEST_SESSION_KEY_FORMAT.format(token)] = session_request.pk
                return redirect()
            else:
                session_url = session.url
                request.session[session_key] = session_url

        return JsonResponse({
            'url': session_url
        })
