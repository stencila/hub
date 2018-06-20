from .common import Common


class Dev(Common):

    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'django_extensions'
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
