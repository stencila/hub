from .common import Common


class Dev(Common):

    DEBUG = True

    SECRET_KEY = 'not-a-secret'
    JWT_SECRET = 'not-a-secret'

    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'django_extensions'
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    AWS_ACCESS_KEY_ID = 'AAA'
    AWS_SECRET_ACCESS_KEY = 'abc123'
    AWS_STORAGE_BUCKET_NAME = 'test.bucket.stenci.la'
