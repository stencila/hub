import time
import typing

import jwt

from django.conf import settings

JWT_ALGORITHM = 'HS256'
JWT_ENCODING = 'utf8'


def jwt_encode(payload: typing.Optional[dict] = None, secret: typing.Optional[str] = None) -> str:
    """Wrap the jwt.encode function to keep algorithms/data consistent throughout the project."""
    if payload is None:
        payload = {}

    if 'iat' not in payload:
        payload['iat'] = time.time()

    if not secret:
        secret = typing.cast(str, settings.JWT_SECRET)

    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM).decode(JWT_ENCODING)
