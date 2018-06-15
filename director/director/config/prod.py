import os

from .common import Common


class Prod(Common):

    DEBUG = False

    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'raven.contrib.django.raven_compat'
    ]

    MIDDLEWARE = Common.MIDDLEWARE + [
        # Placed at the bottom of the middleware stack to catch *any* 404s
        'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware'
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    RAVEN_CONFIG = {
        'dsn': os.getenv('SENTRY_DSN')
    }
