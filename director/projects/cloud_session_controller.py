import enum
import typing
from datetime import timedelta
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.utils import timezone

from projects.client_base import RestClientBase, HttpMethod, SessionAttachContext, SessionInformation, SessionLocation
from projects.models import Project, Session
from projects.session_models import SessionStatus, SessionRequest, SESSION_QUEUE_CHECK_TIMEOUT, \
    SESSION_QUEUE_CREATION_TIMEOUT
from projects.source_operations import generate_project_storage_directory

SESSION_CREATE_PATH_FORMAT = 'execute?waitForReady=false'
SESSION_STATUS_PATH_FORMAT = 'status'


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


class CloudClient(RestClientBase):
    """Client for interaction with Stencila Cloud."""

    class_id = 'CLOUD'

    def get_session_create_url(self, environ: str) -> str:
        return self.get_full_url(SESSION_CREATE_PATH_FORMAT.format(environ))

    @staticmethod
    def transform_session_parameters(session_parameters: dict, environ: str) -> dict:
        """Transform the Hub session parameters into a format that Cloud (Kubernetes) understands."""
        transformed = {}

        for key in ['description', 'lifetime', 'mounts', 'name', 'network', 'timeout']:
            if key in session_parameters:
                transformed[key] = session_parameters[key]

        transformed['environment'] = {'id': environ}

        if 'memory' in session_parameters:
            transformed['ram'] = {'limit': session_parameters['memory']}

        if 'cpu' in session_parameters:
            transformed['cpu'] = {'shares': session_parameters['cpu'] * 1000}

        return transformed

    def generate_location(self, session: Session,
                          authorization_extra_parameters: typing.Optional[dict] = None) -> SessionLocation:
        url_components = urlparse(session.url)
        return SessionLocation(url_components.path, url_components.scheme + '://' + url_components.netloc,
                               self.generate_jwt_token(authorization_extra_parameters))

    def start_session(self, environ: str, session_parameters: dict) -> SessionAttachContext:
        """Start a cloud session and return its URL."""
        result = self.make_request(HttpMethod.PUT, self.get_full_url(SESSION_CREATE_PATH_FORMAT),
                                   body_data=self.transform_session_parameters(session_parameters, environ))

        urls = result.get('urls')

        if urls:
            return SessionAttachContext(urls[0], result.get('executionId', ''))

        path = result.get('path')
        assert path is not None
        return SessionAttachContext(self.get_full_url(path))

    def get_session_info(self, session: Session) -> SessionInformation:
        """Get a dictionary with information about the session. At this stage we are only interested in its status."""
        session_info = self.make_request(HttpMethod.PUT, self.get_full_url(SESSION_STATUS_PATH_FORMAT),
                                         body_data={'id': session.execution_id})
        status = KubernetesPodStatus(session_info['status'].lower())
        return SessionInformation(SESSION_STATUS_LOOKUP[status])


class SessionException(Exception):
    """Generic exception for problems with Session, in particular that there are already enough session running."""


class ActiveSessionsExceededException(SessionException):
    """Raised if there are already too many active `Session`s."""


class CloudSessionFacade(object):
    """Wrap interaction with the Stencila Cloud in a project-centric and Django-reliant way."""

    def __init__(self, project: Project, client: RestClientBase) -> None:
        self.project = project
        self.client = client

    def session_requests_exist(self) -> bool:
        return self.project.session_requests.count() > 0

    def check_session_queue_full(self) -> None:
        """
        Check if we are allowed to create a new `SessionRequest` for the `Project`.

        This method will either complete successfully if we are, or raise a `SessionException` if not.
        """
        if self.project.sessions_queued is None:  # no limit set so always return (success)
            return

        queued_request_count = self.project.session_requests.count()
        if queued_request_count >= self.project.sessions_queued:
            raise SessionException("There are already {}/{} requests for sessions for this project.".format(
                queued_request_count, self.project.sessions_queued))

    def check_total_sessions_exceeded(self) -> None:
        """
        Check if we are allowed to create a new `Session` for the `Project`.

        This checks on the total number of `Session`s that have every been created, not just the active ones.
        This method will either complete successfully if a `Session` can be created, or raise a `SessionException` if
        not.
        """
        if self.project.sessions_total is None:
            # non-failure, Session is not blocked from being created due to total Sessions being exceeded as there is no
            # limit
            return

        total_session_count = self.get_total_session_count()
        if self.project.sessions_total <= total_session_count:
            raise SessionException(
                "Unable to create new sessions for the project. {}/{} have already been created.".format(
                    total_session_count, self.project.sessions_total))

    def check_active_sessions_exceeded(self) -> None:
        """
        Check if we are allowed to create a new `Session` for the `Project`.

        This checks the number of active `Session`s. This method will either complete successfully if a `Session` can be
        created, or raise a `ActiveSessionsExceededException` if not.
        """
        if self.project.sessions_concurrent is None:
            # return non-failure. Session is not blocked from being created due to too many running Sessions as there is
            # no limit
            return

        active_session_count = self.get_active_session_count()

        if self.project.sessions_concurrent <= active_session_count:
            raise ActiveSessionsExceededException(
                "Unable to start session for the project. {}/{} are already active.".format(
                    active_session_count, self.project.sessions_concurrent))

    def check_session_requests_exist(self, session_request_to_use: typing.Optional[SessionRequest]) -> None:
        """
        Check if the `Project` has any `SessionRequest`s.

        If so a new `Session` should not be started (an `ActiveSessionsExceededException` is raised); unless
        `session_request_to_use` is passed in, in which case the `Session` can be created and that `SessionRequest`
        is "used up".

        This method should only be called after the other checks for total sessions and active sessions being exceeded
        have been executed.
        """
        if session_request_to_use:
            session_request_to_use.delete()  # consider this `SessionRequest` to be used up, so remove it
            return

        if self.session_requests_exist():
            # other users are waiting and the current user is not first in queue so queue them up
            raise ActiveSessionsExceededException(
                "Unable to start session for the project as there are already requests queued")

    def create_session_request(self, environ: str) -> SessionRequest:
        self.expire_stale_session_requests()

        self.check_session_queue_full()

        return self.project.session_requests.create(environ=environ)

    def expire_stale_session_requests(self) -> None:
        """
        Expire `SessionRequest`s that have not been checked recently.

        Remove `SessionRequest`s that have not been checked for `SESSION_QUEUE_CHECK_TIMEOUT` seconds, or were
        created more than `SESSION_QUEUE_CREATION_TIMEOUT` seconds ago and have never been checked.
        """
        last_check_before = timezone.now() - timedelta(seconds=SESSION_QUEUE_CHECK_TIMEOUT)
        SessionRequest.objects.filter(project=self.project, last_check__lte=last_check_before).delete()

        creation_before = timezone.now() - timedelta(seconds=SESSION_QUEUE_CREATION_TIMEOUT)
        SessionRequest.objects.filter(project=self.project, created__lte=creation_before,
                                      last_check__isnull=True).delete()

    def check_session_can_start(self, session_request_to_use: typing.Optional[SessionRequest]):
        """Wrap the checks that must be done before allowing a Session to start."""
        self.check_total_sessions_exceeded()
        self.check_active_sessions_exceeded()
        self.check_session_requests_exist(session_request_to_use)

    def perform_session_create(self, environ: str, session_parameters: dict) -> Session:
        """
        Do the actual Session creation without checking if the `Project` limits it.

        Don't call this method unless the check_* methods have already been called.
        """
        session_parameters['mounts'] = [
            self.generate_project_volume_mount()
        ]
        attach_context = self.client.start_session(environ, session_parameters)

        # TODO should we record some of the request
        # headers e.g. `REMOTE_ADDR`, `HTTP_USER_AGENT`, `HTTP_REFERER` for analytics?

        return Session.objects.create(
            project=self.project,
            started=timezone.now(),
            last_check=timezone.now(),
            url=attach_context.url,
            execution_id=attach_context.execution_id,
            client_class_id=self.client.class_id
        )

    def create_session(self, environ: str, session_request_to_use: typing.Optional[SessionRequest] = None) -> Session:
        """
        Create a session for a project on a (remote) Stencila execution Host.

        Usually an instance of `stencila/cloud` but could even be a user's local machine.
        """
        self.poll_sessions()  # make sure there is an up to date picture of Sessions before proceeding
        self.check_session_can_start(session_request_to_use)
        return self.perform_session_create(environ, self.project.session_parameters.serialize())

    def get_active_session_count(self) -> int:
        return Session.objects.filter_project_and_status(self.project, SessionStatus.RUNNING).count()

    def get_total_session_count(self) -> int:
        return self.project.sessions.count()

    def update_session_info(self, session: Session) -> None:
        if session.client_class_id != self.client.class_id:
            # if the session was started with a different client, assume it is lost and stopped.
            session_info = SessionInformation(SessionStatus.STOPPED)
        else:
            try:
                session_info = self.client.get_session_info(session)
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    # Session info is missing - assume it has stopped
                    session.stopped = timezone.now()
                    return
                else:
                    raise

        # This assumes a one-way session flow, Unknown -> Not Started -> Running -> Stopped. Things might go wrong
        # if a session is stopped and then starts running again.

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

    def generate_external_location(self, session: Session,
                                   authorization_extra_parameters: typing.Optional[dict] = None) -> SessionLocation:
        return self.client.generate_location(session, authorization_extra_parameters)

    def generate_project_volume_mount(self) -> dict:
        return {
            "destination": "/work",
            "source": generate_project_storage_directory(settings.STENCILA_REMOTE_PROJECT_STORAGE_DIRECTORY,
                                                         self.project),
            "options": ["rw"]
        }
