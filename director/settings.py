"""
Django settings for director project.

Uses ``django-configurations``. For more on this package, see
https://github.com/jazzband/django-configurations

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import datetime
import os
import warnings

from configurations import Configuration, values

from version import __version__

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
        'drf_yasg',
        'knox',
        'django_filters',
        'django_intercom',
        'djstripe',

        # Our apps

        'users',
        'accounts',
        'projects',
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
                    'lib.template_context_processors.version',
                    'lib.template_context_processors.sentry_dsn',
                    'lib.template_context_processors.posthog_key',
                    'lib.template_context_processors.feature_toggles'
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

    STATIC_URL = values.Value('/static/')

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'assets')
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
        # Use camel casing for everything (inputs and outputs)
        'DEFAULT_RENDERER_CLASSES': (
            'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        ),
        'DEFAULT_PARSER_CLASSES': (
            'djangorestframework_camel_case.parser.CamelCaseJSONParser',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            # Default is for API endpoints to require the user to be authenticated
            'rest_framework.permissions.IsAuthenticated',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            # Default is for token and Django session authentication
            'api.auth.BasicAuthentication',
            'knox.auth.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ),
        'EXCEPTION_HANDLER': 'api.handlers.custom_exception_handler',
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
        'PAGE_SIZE': 50,

        # Use JSON by default when using the test client
        # https://www.django-rest-framework.org/api-guide/testing/#setting-the-default-format
        'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    }

    # django-rest-knox settings for API tokens
    # See http://james1345.github.io/django-rest-knox/settings/
    REST_KNOX = {
        # The Prefix to use in the Authorization header
        'AUTH_HEADER_PREFIX': 'Token',
        # Automatically refresh the token when it is used
        'AUTO_REFRESH': True,
        # Period until token expires.  None will create tokens that never expire.
        'TOKEN_TTL': datetime.timedelta(days=7),
    }

    SWAGGER_SETTINGS = {
        'SECURITY_DEFINITIONS': {
            'API': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header'
            }
        }
    }

    # django-rest-framework-jwt settings for JWT execution session tokens
    # See https://jpadilla.github.io/django-rest-framework-jwt/#additional-settings
    JWT_AUTH = {
        # The Prefix to use in the Authorization header
        'JWT_AUTH_HEADER_PREFIX': 'JWT',
        # Period until token expires. Generally recommended to be <15 mins
        'JWT_EXPIRATION_DELTA': datetime.timedelta(minutes=10),
        # Allow token to be refreshed within a given period from initial issuance
        'JWT_ALLOW_REFRESH': True,
        'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=1),
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

    # Additional middleware only used in development
    MIDDLEWARE = [
                     'debug_toolbar.middleware.DebugToolbarMiddleware',
                 ] + Common.MIDDLEWARE

    # During development just print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # JWT secret (must be overriden in Prod settings, see below)
    JWT_SECRET = values.Value('not-a-secret')

    STENCILA_GITHUB_APPLICATION_NAME = 'Stencila Hub Integration (Test)'
    STENCILA_GITHUB_APPLICATION_URL = 'https://github.com/organizations/stencila/settings/apps/' \
                                      'stencila-hub-integration-test/installations'
    INTERCOM_DISABLED = True


class Prod(Common):
    """Configuration settings used in production at https://hub.stenci.la."""

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
    # in a Docker container (ie. locally not behind a HTTPS load balancer)
    # See `make run-prod`
    SECURE_SSL_REDIRECT = values.BooleanValue(True)

    # Do not redirect the status check to HTTPS so that
    # HTTP health checks will still work.
    SECURE_REDIRECT_EXEMPT = [r'^api/status/?$', r'^/?$']

    # Use unpkg.com CDN to serve static assets
    STATIC_URL = values.Value('https://unpkg.com/@stencila/hub@{}/director/static/'.format(__version__))

    INTERCOM_APPID = values.Value('')

    # JWT secret must be set as environment
    # variable when in production
    JWT_SECRET = values.SecretValue()

    # Use GoogleCloudStorage for uploads
    DEFAULT_FILE_STORAGE = 'lib.storage.CustomPublicGoogleCloudStorage'
    GS_PROJECT_ID = values.Value()
    GS_BUCKET_NAME = values.Value()

    # Use SendGrid for emails
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
    SENDGRID_API_KEY = values.SecretValue()

    # Use Sentry for error reporting
    # Note: The DSN is not a secret https://forum.sentry.io/t/dsn-private-public/6297/2
    SENTRY_DSN = values.Value('https://6329017160394100b21be92165555d72@sentry.io/37250')

    # Use PostHog for product analytics
    POSTHOG_KEY = values.Value('LeXA_J7NbIow0-mEejPwazN7WvZCj-mFKSvLL5oM4w0')

    @classmethod
    def post_setup(cls):
        print(cls.SECURE_SSL_REDIRECT)
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=cls.SENTRY_DSN,
            release='hub@{}'.format(__version__),
            integrations=[DjangoIntegration()],
            send_default_pii=True
        )
