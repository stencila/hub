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
        'django.contrib.sites',  # Required by allauth

        # Third party apps

        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        # Social account providers. See
        #    http://django-allauth.readthedocs.org/en/latest/providers.html
        # When you add an item here you must:
        #   - add an entry in SOCIALACCOUNT_PROVIDERS below
        #   - register Stencila as an API client or app with the provider
        #   - add a SocialApp instance (/admin/socialaccount/socialapp/add/)
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.orcid',
        'allauth.socialaccount.providers.twitter',

        'crispy_forms',
        'crispy_forms_bulma',
        'polymorphic',
        'storages',
        'rest_framework',

        # Our apps

        'users',
        'permissions',
        'accounts',
        'projects',
        'editors',
        'hosts',
        'checkouts'
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
                os.path.join(BASE_DIR, 'templates'),
                # Needed to ensure that allauth templates are overidden by ours
                os.path.join(BASE_DIR, 'users', 'templates')
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

    SITE_ID = 1  # Required by allauth

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

    # Authentication

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    )

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

    LOGIN_URL = '/me/signin'

    LOGIN_REDIRECT_URL = '/'

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
        os.path.join(BASE_DIR, 'assets'),
        os.path.join(BASE_DIR, 'extern')
    ]

    # 'Media' files (uploaded by users)
    # https://docs.djangoproject.com/en/2.0/topics/files/

    MEDIA_ROOT = os.path.join(BASE_DIR, 'storage')

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console'
            }
        },
        'loggers': {
            '': {
                'level': 'WARNING',
                'handlers': ['console']
            },
        }
    }

    # Third-party application settings

    CRISPY_ALLOWED_TEMPLATE_PACKS = ['bulma']
    CRISPY_TEMPLATE_PACK = 'bulma'
    CRISPY_CLASS_CONVERTERS = {
        "checkboxinput": "checkbox"
    }

    # Stencila settings

    # URL of Stencila native execution host
    # This default value is the local evelopment URL for
    # the `stencila/cloud` host
    NATIVE_HOST_URL = values.Value('http://localhost:2000')

    # URL of this application. This is used by editors and other
    # external applications to callback to the director.
    # It needs to be the URL that the user is logged in to
    # the hub so that credentails are sent.
    # This default value is the usual value in development
    CALLBACK_URL = values.Value('http://localhost:3000')

    # Token to restrict signins and singups while beta testing
    BETA_TOKEN = values.Value('abc123')


class Dev(Common):
    """
    Configuration settings used in development
    """

    # Ensure debug is always true in development
    DEBUG = True

    # Crispy forms should fail loudly during development
    CRISPY_FAIL_SILENTLY = not DEBUG

    # This variable must always be set, even in development.
    SECRET_KEY = 'not-a-secret-key'

    # Only allow localhost if in development mode
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

    INTERNAL_IPS = '127.0.0.1'  # For debug_toolbar

    # Additional apps only used in development
    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'debug_toolbar',
        'django_extensions'
    ]

    # Additional middleware only used in development
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + Common.MIDDLEWARE

    # During development just print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # JWT secret can be set but has a default value
    # when in development which is lib with stencila/cloud
    JWT_SECRET = values.Value('not-a-secret')


class Prod(Common):
    """
    Configuration settings used in production
    """

    # Ensure debug is always false in production
    DEBUG = False

    # Require that a `DJANGO_SECRET_KEY` environment
    # variable is set during production
    SECRET_KEY = values.SecretValue()

    # In production, use wildcard because load balancers
    # perform health checks without host specific Host header value
    ALLOWED_HOSTS = ['*']

    # Additional apps only used in production
    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'raven.contrib.django.raven_compat'
    ]

    # JWT secret must be set as environment
    # variable when in production
    JWT_SECRET = values.SecretValue()

    # Ensure that the beta token is set
    BETA_TOKEN = values.SecretValue()

    # Use GoogleCloudStorage for uploads
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_PROJECT_ID = values.Value()
    GS_BUCKET_NAME = values.Value()

    # Use SendGrid for emails
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
    SENDGRID_API_KEY = values.SecretValue()

    # Use Sentry for error reporting
    RAVEN_CONFIG = {
        'dsn': values.Value(environ_name='SENTRY_DSN')
    }
