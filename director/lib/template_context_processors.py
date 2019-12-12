import typing

from django.conf import settings
from django.http import HttpRequest


def sentry_js_url(request: HttpRequest) -> typing.Dict[str, str]:
    return {'SENTRY_JS_URL': settings.SENTRY_JS_URL}


def feature_toggle(request: HttpRequest) -> typing.Dict[str, bool]:
    return {'FEATURE_{}'.format(k): v for k, v in settings.FEATURES.items()}
