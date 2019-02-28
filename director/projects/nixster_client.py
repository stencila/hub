import typing
from urllib.parse import urlparse, quote, urlunparse

from projects.client_base import RestClientBase, HttpMethod, SessionAttachContext, SessionInformation, SessionLocation
from projects.session_models import SessionStatus, Session


def safe_int(v: typing.Any) -> typing.Optional[int]:
    if v is None:
        return None

    try:
        return int(v)
    except ValueError:
        return None


class NixsterClient(RestClientBase):
    class_id = 'NIXSTER'

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

            if 'mounts' in session_parameters:
                request_data['mounts'] = session_parameters['mounts']

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

        response = self.make_request(HttpMethod.POST, self.get_full_url('execute'),
                                     extra_jwt_payload={'cid': container_id}, body_data=request_data)
        return response['output']

    def generate_attach_context(self, environment_id: str, container_id: str) -> SessionAttachContext:
        url_components = list(urlparse(self.get_full_url('interact')))
        url_components[0] = 'ws'
        url_components[4] = 'containerId={}&environment={}'.format(quote(container_id), quote(environment_id))

        return SessionAttachContext(urlunparse(url_components), container_id)

    def start_session(self, environ: str, session_parameters: dict) -> SessionAttachContext:
        container_id = self.start_container(environ, session_parameters)
        return self.generate_attach_context(environ, container_id)

    def generate_location(self, session: Session,
                          authorization_extra_parameters: typing.Optional[dict] = None) -> SessionLocation:
        execution_id = session.execution_id

        if self.server_proxy_path:
            host = None
            path = self.server_proxy_path
        else:
            host = self.server_host
            path = ''

        separator = '' if path.endswith('/') else '/'

        if not authorization_extra_parameters:
            authorization_extra_parameters = {}

        authorization_extra_parameters['cide'] = execution_id

        token = self.generate_jwt_token(authorization_extra_parameters)

        path += '{}interact?containerId={}&token={}'.format(
            separator,
            quote(execution_id),
            token
        )
        return SessionLocation(path, host, token)

    def get_session_info(self, session: Session) -> SessionInformation:
        container_id = session.execution_id

        if not container_id:
            return SessionInformation(SessionStatus.STOPPED)  # If we have no container_id then it must not be running

        request_data = {
            'environmentId': 'multi-mega',  # TODO: this should not be required on front or backend
            'containerId': container_id
        }

        response = self.make_request(HttpMethod.POST, self.get_full_url('container-status'),
                                     extra_jwt_payload={'cid': session.execution_id}, body_data=request_data)

        if response['status'] == 'RUNNING':
            return SessionInformation(SessionStatus.RUNNING)

        if response['status'] == 'STOPPED':
            return SessionInformation(SessionStatus.STOPPED)

        return SessionInformation(SessionStatus.UNKNOWN)
