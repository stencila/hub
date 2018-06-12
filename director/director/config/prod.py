import os
import raven

from .common import Common, external_keys


class Prod(Common):

    DEBUG = False

    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'raven.contrib.django.raven_compat'
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    RAVEN_CONFIG = {
        'dsn': os.getenv('SENTRY_DSN')
    }

    @classmethod
    def post_setup(cls):
        """Raise an exception if a setting is missing or empty string"""
        super(Prod, cls).post_setup()
        for key in external_keys:
            if not getattr(cls, key, '').strip():
                raise RuntimeError("Missing setting: %s" % key)
