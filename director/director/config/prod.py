from configurations import values
from .common import Common


class Prod(Common):

    DEBUG = False

    SECRET_KEY = values.Value(None, environ_required=True)
    JWT_SECRET = values.Value(None, environ_required=True)

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    AWS_ACCESS_KEY_ID = values.Value('AAA')
    AWS_SECRET_ACCESS_KEY = values.Value('abc123')
    AWS_STORAGE_BUCKET_NAME = values.Value('bucket.stenci.la')
