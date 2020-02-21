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
import sys
import warnings
from configurations import Configuration, values

# TODO: the UserWarning might start to not be raised as of psycopg2 v2.8+ but until then suppress it
warnings.filterwarnings('ignore', category=UserWarning, module='psycopg2')


class Common(Configuration):
    """Configuration settings common to both development and production."""

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
        'django.contrib.humanize',

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

        'avatar',
        'crispy_forms',
        'crispy_forms_bulma',
        'polymorphic',
        'storages',
        'rest_framework',
        'django_intercom',
        'djstripe',

        # Our apps

        'stencila_admin',  # not Django admin
        'users',
        'accounts',
        'projects',
        'editors',
        'hosts',
        'checkouts',
        'stencila_open'
    ]

    MIDDLEWARE = [
        'lib.middleware.ie_detect_middleware',
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
                    'lib.template_context_processors.sentry_js_url',
                    'lib.template_context_processors.feature_toggle'
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

    DEFAULT_FROM_EMAIL = values.Value('')

    # Authentication

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    )

    ACCOUNT_EMAIL_REQUIRED = True  # tell allauth to require an email address when signing up

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

    TESTING = False

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
    MEDIA_URL = '/media/'

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
        "checkboxinput": "checkbox",
        "numberinput": "input",
    }

    AVATAR_GRAVATAR_DEFAULT = 'identicon'

    # Stencila settings

    EXECUTION_SERVER_HOST = values.Value()
    EXECUTION_SERVER_PROXY_PATH = values.Value()
    EXECUTION_CLIENT = values.Value('NIXSTER')

    # URL of this application. This is used by editors and other
    # external applications to callback to the director.
    # It needs to be the URL that the user is logged in to
    # the hub so that credentils are sent.
    # This default value is the usual value in development
    CALLBACK_URL = values.Value('http://localhost:3000')

    # Token to restrict signins and signups while beta testing
    BETA_TOKEN = values.Value('abc123')

    GS_PUBLIC_READABLE_PATHS = ['avatars/*']
    # these paths will be made publicly readable in the Google Storage bucket after being written to

    STENCILA_GITHUB_APPLICATION_NAME = values.Value('INSERT A REAL APP NAME HERE Stencila Github Integration')
    STENCILA_GITHUB_APPLICATION_URL = values.Value('INSERT A REAL URL HERE '
                                                   'https://github.com/settings/apps/stencila/installations')

    # Path to store project pulls for the hub
    STENCILA_PROJECT_STORAGE_DIRECTORY = values.Value('')

    # Path where the remote executor can find the above Project pulls.
    # By default this is the same as the path in the hub
    STENCILA_REMOTE_PROJECT_STORAGE_DIRECTORY = values.Value(STENCILA_PROJECT_STORAGE_DIRECTORY)

    # URL for Sentry JS error reporting
    SENTRY_JS_URL = values.Value('')

    # This can be any format, it's not used in code, only humans will be looking at this
    STENCILA_HUB_VERSION = values.Value('')

    # some XML files are quite large (3MB+), this basically sets the size of the POST allowed
    DATA_UPLOAD_MAX_MEMORY_SIZE = values.IntegerValue(5 * 1024 * 1024)

    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'SCOPE': [
                'profile',
                'email',
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ],
            'AUTH_PARAMS': {
                'access_type': 'offline'
            }
        }
    }

    STENCILA_BINARY = values.ListValue(['/usr/local/bin/stencila'])
    STENCILA_CLIENT_USER_AGENT = values.Value('Stencila Hub HTTP Client')
    INTERCOM_ACCESS_TOKEN = values.Value('')

    EXECUTA_HOSTS = values.SingleNestedTupleValue('')
    SPARKLA_PROJECT_ROOT = values.Value('')

    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
            'rest_framework.authentication.SessionAuthentication'
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
        'PAGE_SIZE': 100
    }

    STRIPE_LIVE_PUBLIC_KEY = values.Value('')
    STRIPE_LIVE_SECRET_KEY = values.Value('sk_live_test')  # Leaving this blank causes issues running Django
    STRIPE_TEST_PUBLIC_KEY = values.Value('')
    STRIPE_TEST_SECRET_KEY = values.Value('sk_test_test')  # Leaving this blank causes issues running Django
    STRIPE_LIVE_MODE = values.BooleanValue(False)
    DJSTRIPE_WEBHOOK_VALIDATION = None

    # Rudimentary feature toggle
    FEATURES = {
        'PROJECT_SESSION_SETTINGS': False
    }


class Dev(Common):
    """Configuration settings used in development."""

    # Ensure debug is always true in development
    DEBUG = True

    # Crispy forms should fail loudly during development
    CRISPY_FAIL_SILENTLY = not DEBUG

    # This variable must always be set, even in development.
    SECRET_KEY = 'not-a-secret-key'

    # Only allow localhost if in development mode
    ALLOWED_HOSTS = ['*']

    INTERNAL_IPS = '127.0.0.1'  # For debug_toolbar

    # Additional apps only used in development
    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'debug_toolbar',
        'django_extensions'
    ]

    TESTING = sys.argv[1:2] == ['test']

    if TESTING:
        INSTALLED_APPS.append('django_nose')

    # Additional middleware only used in development
    MIDDLEWARE = [
                     'debug_toolbar.middleware.DebugToolbarMiddleware',
                 ] + Common.MIDDLEWARE

    # During development just print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # JWT secret can be set but has a default value
    # when in development which is shared with stencila/cloud
    JWT_SECRET = values.Value('not-a-secret')

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

    NOSE_ARGS = [
        '--with-coverage',
        '--cover-package=projects.cloud_session_controller',
        '--cover-package=projects.views.project_host_views',
        '--cover-package=projects.source_operations',
        '--cover-package=projects.source_forms',
        '--cover-html',
        '--cover-html-dir=' + os.path.join(Common.BASE_DIR, 'coverage'),
        '--cover-xml',
        '--cover-xml-file=' + os.path.join(Common.BASE_DIR, 'coverage.xml')
    ]

    STENCILA_GITHUB_APPLICATION_NAME = 'Stencila Hub Integration (Test)'
    STENCILA_GITHUB_APPLICATION_URL = 'https://github.com/organizations/stencila/settings/apps/' \
                                      'stencila-hub-integration-test/installations'
    INTERCOM_DISABLED = True


class Prod(Common):
    """Configuration settings used in production (and staging)."""

    # Ensure debug is always false in production
    DEBUG = False

    # Require that a `DJANGO_SECRET_KEY` environment
    # variable is set during production
    SECRET_KEY = values.SecretValue()

    # In production, use wildcard because load balancers
    # perform health checks without host specific Host header value
    ALLOWED_HOSTS = ['*']

    # It is being run behind Google Cloud Load Balancer, so look for this header
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Enforce HTTPS
    # Allow override to be able to test other prod settings during development
    # in a Docker container (ie. locallocally not behind a HTTPS load balancer)
    # See `make director-rundocker`
    SECURE_SSL_REDIRECT = values.BooleanValue(True)

    SECURE_REDIRECT_EXEMPT = [r'^system-status/$']

    # Additional apps only used in production
    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'raven.contrib.django.raven_compat'
    ]

    INTERCOM_APPID = values.Value('')
    # JWT secret must be set as environment
    # variable when in production
    JWT_SECRET = values.SecretValue()

    # Ensure that the beta token is set
    BETA_TOKEN = values.SecretValue()

    # Use GoogleCloudStorage for uploads
    DEFAULT_FILE_STORAGE = 'lib.storage.CustomPublicGoogleCloudStorage'
    GS_PROJECT_ID = values.Value()
    GS_BUCKET_NAME = values.Value()

    # Use SendGrid for emails
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
    SENDGRID_API_KEY = values.SecretValue()

    # Use Sentry for error reporting
    RAVEN_CONFIG = {
        'dsn': values.Value(environ_name='SENTRY_DSN')
    }
