import enum
import time
import typing
from urllib.parse import urljoin

import jwt
import requests
from django.utils import timezone

from projects.models import Project, Session
from projects.session_models import SessionStatus

JWT_ALGORITHM = "HS256"
SESSION_CREATE_PATH_FORMAT = "sessions/{}"


class HttpMethod(enum.Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'


class KubernetesPodStatus(enum.Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    UNKNOWN = 'unknown'


SESSION_STATUS_LOOKUP = {
    KubernetesPodStatus.PENDING: SessionStatus.NOT_STARTED,
    KubernetesPodStatus.RUNNING: SessionStatus.RUNNING,
    KubernetesPodStatus.SUCCEEDED: SessionStatus.STOPPED,
    KubernetesPodStatus.FAILED: SessionStatus.STOPPED,
    KubernetesPodStatus.UNKNOWN: SessionStatus.UNKNOWN
}


class SessionInformation(typing.NamedTuple):
    status: SessionStatus  # This is probably only going to be RUNNING or STOPPED


class CloudClient(object):
    """Client for interaction with Stencila Cloud"""

    def __init__(self, host_url: str, jwt_secret: str):
        self.host_url = host_url + "/" if not host_url.endswith("/") else host_url  # ensure trailing /
        self.jwt_secret = jwt_secret

    def generate_jwt_token(self) -> str:
        """"Create a JWT token for the host"""
        jwt_payload = {"iat": time.time()}
        return jwt.encode(jwt_payload, self.jwt_secret, algorithm=JWT_ALGORITHM).decode("utf-8")

    def get_authorization_header(self) -> typing.Dict[str, str]:
        return {
            "Authorization": "Bearer {}".format(self.generate_jwt_token())
        }

    def make_request(self, method: HttpMethod, url: str, body_data: typing.Optional[dict] = None) -> dict:
        # TODO: add `SessionParameters` to the POST body (currently they won't do anything anyway)
        response = requests.request(method.value, url, headers=self.get_authorization_header(), json=body_data)
        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            raise Exception('Error parsing body: ' + response.text)

    def get_full_url(self, path: str) -> str:
        return urljoin(self.host_url, path)

    def get_session_create_url(self, environ: str) -> str:
        return self.get_full_url(SESSION_CREATE_PATH_FORMAT.format(environ))

    def start_session(self, environ: str, session_parameters: dict) -> str:
        """Start a cloud session and return its URL"""
        result = self.make_request(HttpMethod.POST, self.get_session_create_url(environ), session_parameters)

        session_url = result.get('url')

        if session_url is not None:
            return session_url

        path = result.get('path')
        assert path is not None
        return self.get_full_url(path)

    def get_session_info(self, session_url: str) -> SessionInformation:
        """Get a dictionary with information about the session. At this stage we are only interested in its status."""
        session_info = self.make_request(HttpMethod.GET, session_url)
        status = KubernetesPodStatus(session_info['status'].lower())
        return SessionInformation(SESSION_STATUS_LOOKUP[status])


class SessionException(Exception):
    """Generic exception for problems with Session, in particular that there are already enough session running."""
    pass


class CloudSessionFacade(object):
    """Wrap interaction with the Stencila Cloud in a project-centric and Django-reliant way."""

    def __init__(self, project: Project, client: CloudClient):
        self.project = project
        self.client = client

    def create_session(self, environ: str) -> Session:
        """
        Create a session for a project on a remote Stencila execution Host (usually
        an instance of `stencila/cloud` but could even be a user's local machine)
        """
        self.poll_sessions()  # make sure there is an up to date picture of Sessions before proceeding

        active_session_count = self.get_active_session_count()
        total_session_count = self.get_total_session_count()

        if self.project.sessions_total is not None and self.project.sessions_total <= total_session_count:
            raise SessionException(
                "Unable to create new sessions for the project. {}/{} have already been created.".format(
                    total_session_count, self.project.sessions_total))

        if self.project.sessions_concurrent is not None and self.project.sessions_concurrent <= active_session_count:
            raise SessionException(
                "Unable to start session for the project. {}/{} are already active.".format(
                    active_session_count, self.project.sessions_concurrent))

        session_url = self.client.start_session(environ, self.project.session_parameters.serialize())

        # TODO should we record some of the request
        # headers e.g. `REMOTE_ADDR`, `HTTP_USER_AGENT`, `HTTP_REFERER` for analytics?

        return Session.objects.create(
            project=self.project,
            started=timezone.now(),
            last_check=timezone.now(),
            url=session_url
        )

    def get_active_session_count(self) -> int:
        return Session.objects.filter_project_and_status(self.project, SessionStatus.RUNNING)

    def get_total_session_count(self) -> int:
        return Session.objects.filter(project=self.project)

    def update_session_info(self, session: Session) -> None:
        session_info = self.client.get_session_info(session.url)

        # This assumes a one-way session flow, Unknown -> Not Started -> Running -> Stopped. Things might go wrong if
        # a session is stopped and then starts running again.

        if session_info.status != SessionStatus.UNKNOWN:
            # Don't update the last check if the status of the container is not known
            session.last_check = timezone.now()

        if not session.started and session_info.status == SessionStatus.RUNNING:
            # Set Session start time if it is now stopped and we haven't previously recorded that
            session.started = timezone.now()

        if not session.stopped and session_info.status == SessionStatus.STOPPED:
            # Set Session stop time if it is now stopped and we haven't previously recorded that
            session.stopped = timezone.now()

    def poll_sessions(self) -> None:
        for session in Session.objects.filter_stale_status().filter(project=self.project):
            self.update_session_info(session)
            session.save()
