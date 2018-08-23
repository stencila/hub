import enum
import time
import typing
from urllib.parse import urljoin

import jwt
import requests
from django.utils import timezone

from projects.models import Project, Session

JWT_ALGORITHM = "HS256"
SESSION_CREATE_PATH_FORMAT = "sessions/{}"


class HttpMethod(enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


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

    def make_request(self, method: HttpMethod, url: str) -> dict:
        # TODO: add `SessionParameters` to the POST body (currently they won't do anything anyway)
        response = requests.request(method.value, url, headers=self.get_authorization_header())
        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            raise Exception('Error parsing body: ' + response.text)

    def get_full_url(self, path: str) -> str:
        return urljoin(self.host_url, path)

    def get_session_create_url(self, environ: str) -> str:
        return self.get_full_url(SESSION_CREATE_PATH_FORMAT.format(environ))

    def start_session(self, environ: str) -> str:
        result = self.make_request(HttpMethod.POST, self.get_session_create_url(environ))

        session_url = result.get('url')

        if session_url is not None:
            return session_url

        path = result.get('path')
        assert path is not None
        return self.get_full_url(path)


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
        # TODO check the total number and number of concurrent sessions for project

        session_url = self.client.start_session(environ)

        # TODO should we record some of the request
        # headers e.g. `REMOTE_ADDR`, `HTTP_USER_AGENT`, `HTTP_REFERER` for analytics?

        return Session.objects.create(
            project=self.project,
            started=timezone.now(),
            last_check=timezone.now(),
            url=session_url
        )

    def get_active_session_count(self) -> int:
        raise NotImplementedError("Implement counting of active sessions for project")

    def get_total_session_count(self) -> int:
        raise NotImplementedError("Implement counting of all sessions for project")

    def update_session_info(self, session: Session) -> None:
        raise NotImplementedError("Implement fetching the Session info")

    def poll_session(self) -> None:
        raise NotImplementedError("Implement polling all the sessions in the project (that haven't been polled for X "
                                  "minutes)")
