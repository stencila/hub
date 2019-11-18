import enum
import os
import typing

from django.conf import settings
import stencila.schema.types

from lib.jwt import jwt_encode
from lib.resource_allowance import account_resource_limit_multiple, QuotaName
from projects.project_models import Project


class SparklaEnvironment(enum.Enum):
    ALPINE = 'stencila/sparkla-alpine'
    UBUNTU = 'stencila/sparkla-ubuntu'
    UBUNTU_MIDI = 'stencila/sparkla-ubuntu-midi'


DEFAULT_ENVIRONMENT = SparklaEnvironment.UBUNTU_MIDI


def to_dict(node: stencila.schema.types.Entity) -> typing.Any:
    if not isinstance(node, stencila.schema.types.Entity):
        return node

    node_dict = {
        'type': node.__class__.__name__
    }

    for k, v in vars(node).items():
        if isinstance(v, stencila.schema.types.Entity):
            node_dict[k] = to_dict(v)
        elif isinstance(v, list):
            node_dict[k] = list(map(to_dict, v))
        elif isinstance(v, dict):
            node_dict[k] = {k1: to_dict(v1) for k1, v1 in v.items()}
        else:
            node_dict[k] = v

    return node_dict


def generate_jwt(jwt_secret: str, url: str, user_id: str, environment_id: SparklaEnvironment = DEFAULT_ENVIRONMENT,
                 project: typing.Optional[Project] = None, project_id_override: typing.Optional[str] = None) -> str:
    if not settings.SPARKLA_PROJECT_ROOT:
        raise ValueError('SPARKLA_PROJECT_ROOT is empty.')

    environment = stencila.schema.types.SoftwareEnvironment(environment_id.value)

    software_session = stencila.schema.types.SoftwareSession(environment=environment)

    limits: typing.Dict[str, typing.Any] = {
        'url': url,
        'userId': user_id
    }

    if project_id_override:
        limits['projectId'] = project_id_override
    elif project:
        account = project.account
        resource_limits = account_resource_limit_multiple(account, {
            QuotaName.MAX_SESSION_DURATION,
            QuotaName.SESSION_MEMORY_LIMIT,
            QuotaName.SESSION_CPU_LIMIT,
            QuotaName.MAX_CLIENTS_PER_SESSION
        })

        if resource_limits[QuotaName.MAX_SESSION_DURATION] != -1:
            limits['sessionDuration'] = resource_limits[QuotaName.MAX_SESSION_DURATION]

        if resource_limits[QuotaName.MAX_CLIENTS_PER_SESSION] != -1:
            limits['clientsPerSession'] = resource_limits[QuotaName.MAX_CLIENTS_PER_SESSION]

        if resource_limits[QuotaName.SESSION_MEMORY_LIMIT] != -1:
            software_session.memoryLimit = resource_limits[QuotaName.SESSION_MEMORY_LIMIT]

        if resource_limits[QuotaName.SESSION_CPU_LIMIT] != -1:
            software_session.cpuLimit = resource_limits[QuotaName.SESSION_CPU_LIMIT]

        limits['projectId'] = project.id
        project_dir = os.path.join(settings.SPARKLA_PROJECT_ROOT, '{}'.format(project.pk))
        software_session.volumeMounts = [stencila.schema.types.VolumeMount('/project', mountSource=project_dir)]

    limits['session'] = to_dict(software_session)

    return jwt_encode(limits, jwt_secret)


def generate_manifest(user_id: str, environment_id: SparklaEnvironment = DEFAULT_ENVIRONMENT,
                      project: typing.Optional[Project] = None,
                      project_id_override: typing.Optional[str] = None) -> typing.List[typing.Dict[str, str]]:
    """Generate a manifest for Sparkla, using the environment, project and user_id to generate the JWT it includes."""
    if not settings.EXECUTA_HOSTS:
        raise ValueError('EXECUTA_HOSTS setting is empty.')

    return [
        {
            'url': url,
            'jwt': generate_jwt(jwt_secret, url, user_id, environment_id, project, project_id_override)
        }
        for url, jwt_secret in settings.EXECUTA_HOSTS
    ]
