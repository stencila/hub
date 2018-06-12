import os
from .common import Common, external_keys


class Prod(Common):

    DEBUG = False

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    @classmethod
    def post_setup(cls):
        """Raise an exception if a setting is missing or empty string"""
        super(Prod, cls).post_setup()
        for key in external_keys:
            if not getattr(cls, key, '').strip():
                raise RuntimeError("Missing setting: %s" % key)
