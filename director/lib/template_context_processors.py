import typing

from django.conf import settings
from django.http import HttpRequest

from version import __version__


def version(request: HttpRequest) -> typing.Dict[str, str]:
    """Set the Stencila Hub version."""
    return {"VERSION": __version__}


def sentry_dsn(request: HttpRequest) -> typing.Dict[str, str]:
    """Set the Sentry DSN for logging of Javascript errors."""
    return {"SENTRY_DSN": getattr(settings, "SENTRY_DSN", None)}


def posthog_key(request: HttpRequest) -> typing.Dict[str, str]:
    """Set the PostHog API key for product analytics."""
    return {"POSTHOG_KEY": getattr(settings, "POSTHOG_KEY", None)}


def feature_toggles(request: HttpRequest) -> typing.Dict[str, bool]:
    """Set feature toggle variables."""
    return {"FEATURE_{}".format(k): v for k, v in settings.FEATURES.items()}
