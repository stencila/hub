import enum
import os
import typing

from django.conf import settings
import stencila.schema.types

from lib.jwt import jwt_encode
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


def generate_jwt(user_id: str, environment_id: SparklaEnvironment = DEFAULT_ENVIRONMENT,
                 project: typing.Optional[Project] = None, project_id_override: typing.Optional[str] = None) -> str:
    if not settings.SPARKLA_JWT_SECRET:
        raise ValueError('SPARKLA_JWT_SECRET is empty.')

    if not settings.SPARKLA_PROJECT_ROOT:
        raise ValueError('SPARKLA_PROJECT_ROOT is empty.')

    environment = stencila.schema.types.SoftwareEnvironment(environment_id.value)

    software_session = stencila.schema.types.SoftwareSession(environment=environment)

    limits = {
        'uid': user_id,
    }

    if project:
        limits['project_id'] = project.id
        project_dir = os.path.join(settings.SPARKLA_PROJECT_ROOT, '{}'.format(project.pk))
        software_session.volumeMounts = [stencila.schema.types.VolumeMount('/project', mountSource=project_dir)]

    if project_id_override:
        limits['project_id'] = project_id_override

    limits['session'] = to_dict(software_session)

    return jwt_encode(limits, settings.SPARKLA_JWT_SECRET)


def generate_manifest(user_id: str, environment_id: SparklaEnvironment = DEFAULT_ENVIRONMENT,
                      project: typing.Optional[Project] = None,
                      project_id_override: typing.Optional[str] = None) -> dict:
    """Generate a manifest for Sparkla, using the environment, project and user_id to generate the JWT it includes."""
    if not settings.SPARKLA_HOST:
        raise ValueError('SPARKLA_HOST setting is empty.')

    return {
        'capabilities': {
            'execute': {
                'required': ['node'],
                'properties': {
                    'node': {
                        'type': 'object',
                        'required': ['type', 'programmingLanguage'],
                        'properties': {
                            'type': {
                                'enum': ['CodeChunk', 'CodeExpression']
                            },
                            'programmingLanguage': {
                                'enum': ['python', 'r']
                            }
                        }
                    }
                }
            }
        },
        'addresses': {
            'ws': {
                'type': 'ws',
                'host': settings.SPARKLA_HOST,
                'port': settings.SPARKLA_PORT,
                'jwt': generate_jwt(user_id, environment_id, project, project_id_override)
            }
        }
    }
