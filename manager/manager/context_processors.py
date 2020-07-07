"""
Functions for defining template rendering contexts.

Each function defines variables that will be available to be
used in templates. Grouped into functions by type of variable.
Prefer adding a variable to an existing function, rather than
creating a new function. If you do create a function make sure
to add it to `TEMPLATES.OPTIONS.context_processors` in `settings.py`.
"""
import typing

from django import conf
from django.http import HttpRequest

from manager.version import __version__


def versions(request: HttpRequest) -> typing.Dict[str, str]:
    """Versions of the Hub and dependencies."""
    return {"VERSION": __version__}


def settings(request: HttpRequest) -> typing.Dict[str, str]:
    """Public (i.e. NOT secret) settings."""
    return {
        "SENTRY_DSN": getattr(conf.settings, "SENTRY_DSN", None),
        "POSTHOG_KEY": getattr(conf.settings, "POSTHOG_KEY", None),
    }
