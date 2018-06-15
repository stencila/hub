import os

from .common import Common


class Prod(Common):

    DEBUG = False

    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'raven.contrib.django.raven_compat'
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    RAVEN_CONFIG = {
        'dsn': os.getenv('SENTRY_DSN')
    }
