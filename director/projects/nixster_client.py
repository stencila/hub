import typing
from urllib.parse import urlparse, quote, urlunparse

from projects.client_base import RestClientBase, HttpMethod, SessionAttachContext, SessionInformation
from projects.session_models import SessionStatus


def safe_int(v: typing.Any) -> typing.Optional[int]:
    if v is None:
        return None

    try:
        return int(v)
    except ValueError:
        return None


class NixsterClient(RestClientBase):
    def start_container(self, environment_id: str, session_parameters: typing.Optional[dict] = None,
                        command: typing.Optional[str] = None) -> str:
        request_data = {'environmentId': environment_id}

        if command:
            request_data['command'] = command

        if session_parameters:
            cpu_shares = safe_int(session_parameters.get('cpu'))
            if cpu_shares is not None:
                request_data['cpuShares'] = '{}'.format(cpu_shares * 1024)  # CPU priority is per 1024

            memory_limit = safe_int(session_parameters.get('memory'))
            if memory_limit is not None:
                request_data['memoryLimit'] = '{}'.format(memory_limit * 1024 * 1024 * 1024)  # bytes to GB

        result = self.make_request(HttpMethod.POST, self.get_full_url('start'), body_data=request_data)
        return result['containerId']

    def stop_container(self, environment_id: str, container_id: str) -> None:
        request_data = {
            'environmentId': environment_id,
            'containerId': container_id
        }
        self.make_request(HttpMethod.POST, self.get_full_url('stop'), extra_jwt_payload={'cid': container_id},
                          body_data=request_data)

    def execute(self, environment_id: str, container_id: str, command: str) -> str:
        request_data = {
            'environmentId': environment_id,
            'containerId': container_id,
            'command': command
        }

        result = self.make_request(HttpMethod.POST, self.get_full_url('execute'),
                                   extra_jwt_payload={'cid': container_id}, body_data=request_data)
        return result['output']

    def generate_attach_context(self, environment_id: str, container_id: str) -> SessionAttachContext:
        url_components = list(urlparse(self.get_full_url('interact')))
        url_components[0] = 'ws'
        url_components[4] = 'containerId={}&environment={}'.format(quote(container_id), quote(environment_id))

        return SessionAttachContext(urlunparse(url_components), container_id)

    def start_session(self, environ: str, session_parameters: dict) -> SessionAttachContext:
        container_id = self.start_container(environ, session_parameters)
        return self.generate_attach_context(environ, container_id)

    def generate_authorization_token(self, execution_id: typing.Optional[str]) -> str:
        """Intended to be overridden but a safe default."""
        return self.generate_jwt_token({'cid': execution_id})

    def get_session_info(self, session_url: str) -> SessionInformation:
        return SessionInformation(SessionStatus.STOPPED)  # TODO: implement this and the backend
