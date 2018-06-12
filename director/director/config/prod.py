from configurations import values
from .common import Common


class Prod(Common):

    DEBUG = False
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
