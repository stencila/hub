from configurations import values
from .common import Common


class Dev(Common):

    DEBUG = True

    SECRET_KEY = 'not-a-secret'
    JWT_SECRET = 'not-a-secret'

    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'django_extensions'
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    AWS_ACCESS_KEY_ID = values.Value('AAA')
    AWS_SECRET_ACCESS_KEY = values.Value('abc123')
    AWS_STORAGE_BUCKET_NAME = values.Value('bucket.stenci.la')
