"""
Django settings for director project.

Uses ``django-configurations``. For more on this package, see
https://github.com/jazzband/django-configurations

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from configurations import Configuration, values


class Common(Configuration):
    """
    Configuration settings common to both development and production
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Application definition

    INSTALLED_APPS = [
        # Django contrib apps
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # Third party apps
        'polymorphic',
        'rest_framework',

        # Our apps
        'projects',
        'editors'
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(BASE_DIR, 'templates')
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/2.0/ref/settings/#databases
    #
    # Defaults to `db.sqlite3` but can be set using `DJANGO_DATABASE_URL` env var
    # Note that the three leading slashes are *intentional*
    # See https://github.com/kennethreitz/dj-database-url#url-schema
    DATABASES = values.DatabaseURLValue(
        'sqlite:///%s/db.sqlite3' % BASE_DIR,
        environ_prefix='DJANGO'  # For consistent naming with other env vars
    )

    # Password validation
    # https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/2.0/topics/i18n/

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/

    # Can be set using `DJANGO_STATIC_URL` env var
    STATIC_URL = values.Value('/static/')

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'assets')
    ]

    # 'Media' files (uploaded by users)
    # https://docs.djangoproject.com/en/2.0/topics/files/

    MEDIA_ROOT = os.path.join(BASE_DIR, 'storage')


class Dev(Common):
    """
    Configuration settings used in development
    """

    # Ensure debug is always true in development
    DEBUG = True

    # This variable must always be set, even in development.
    SECRET_KEY = 'not-a-secret-key'

    # Only allow localhost if in development mode
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

    # Additional apps only used in development
    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'django_extensions'
    ]


class Prod(Common):
    """
    Configuration settings used in production
    """

    # Ensure debug is always false in production
    DEBUG = False

    # Require that a `DJANGO_SECRET_KEY` environment
    # variable is set during production
    SECRET_KEY = values.SecretValue()

    # Allow for development, staging and full production hosts
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'hub-test.stenci.la', 'hub.stenci.la']
