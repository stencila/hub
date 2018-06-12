from configurations import values
from .common import Common


class Dev(Common):

    DEBUG = True

    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'django_extensions'
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

