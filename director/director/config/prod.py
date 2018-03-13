from configurations import values
from .common import Common


class Prod(Common):

    DEBUG = False

    SECRET_KEY = values.Value(None, environ_required=True)
    JWT_SECRET = values.Value(None, environ_required=True)

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
