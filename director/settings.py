"""
Django settings for director project.

Uses ``django-configurations``. For more on this package, see
https://github.com/jazzband/django-configurations

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import datetime
import os

from configurations import Configuration, values

from version import __version__


class Prod(Configuration):
    """
    Configuration settings used in production.

    This should include all the settings needed in production.
    To keep `Dev` and `Test` settings as close as possible to those
    in production we use `Prod` as a base and only override as needed.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    ###########################################################################
    # Core Django settings
    #
    # For a complete list see https://docs.djangoproject.com/en/2.2/ref/settings/
    ###########################################################################

    # Ensure debug is always false in production (overridden in development)
    DEBUG = False

    # Require that a `DJANGO_SECRET_KEY` environment
    # variable is set during production
    SECRET_KEY = values.SecretValue()

    # In production, use wildcard because load balancers
    # perform health checks without host specific Host header value
    ALLOWED_HOSTS = ["*"]

    # It is being run behind Google Cloud Load Balancer, so look for this header
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Enforce HTTPS
    # Allow override to be able to test other prod settings during development
    # in a Docker container (ie. locally not behind a HTTPS load balancer)
    # See `make run-prod`
    SECURE_SSL_REDIRECT = values.BooleanValue(True)

    # Do not redirect the status check to HTTPS so that
    # HTTP health checks will still work.
    SECURE_REDIRECT_EXEMPT = [r"^api/status/?$", r"^/?$"]

    INSTALLED_APPS = [
        # Django contrib apps
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",  # Required by allauth
        "django.contrib.humanize",
        # Third party apps
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
        # Social account providers. See
        #    http://django-allauth.readthedocs.org/en/latest/providers.html
        # When you add an item here you must:
        #   - add an entry in SOCIALACCOUNT_PROVIDERS below
        #   - register Stencila as an API client or app with the provider
        #   - add a SocialApp instance (/admin/socialaccount/socialapp/add/)
        "allauth.socialaccount.providers.github",
        "allauth.socialaccount.providers.google",
        "allauth.socialaccount.providers.orcid",
        "allauth.socialaccount.providers.twitter",
        "avatar",
        "crispy_forms",
        "crispy_forms_bulma",
        "polymorphic",
        "storages",
        "rest_framework",
        "drf_yasg",
        "knox",
        "django_celery_beat",
        "django_filters",
        "django_intercom",
        "djstripe",
        # Our apps
        # Uses dotted paths to AppConfig subclasses as
        # recommended in https://docs.djangoproject.com/en/2.2/ref/applications/#configuring-applications
        "users.apps.UsersConfig",
        "accounts.apps.AccountsConfig",
        "projects.apps.ProjectsConfig",
        "stencila_open.apps.StencilaOpenConfig",
        "jobs.apps.JobsConfig",
    ]

    MIDDLEWARE = [
        "lib.middleware.ie_detect_middleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [
                os.path.join(BASE_DIR, "templates"),
                # Needed to ensure that allauth templates are overidden by ours
                os.path.join(BASE_DIR, "users", "templates"),
            ],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "lib.template_context_processors.versions",
                    "lib.template_context_processors.settings",
                    "lib.template_context_processors.features",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "wsgi.application"

    SITE_ID = 1  # Required by allauth

    # Database defaults to `dev.sqlite3` but can be set using `DATABASE_URL` env var
    # Note that the three leading slashes are *intentional*
    # See https://github.com/kennethreitz/dj-database-url#url-schema
    DATABASES = values.DatabaseURLValue(
        "sqlite:///{}".format(os.path.join(BASE_DIR, "dev.sqlite3"))
    )

    DEFAULT_FROM_EMAIL = values.Value("hello@stenci.la")

    # Authentication

    AUTHENTICATION_BACKENDS = (
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    )

    ACCOUNT_EMAIL_REQUIRED = (
        True  # tell allauth to require an email address when signing up
    )

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    LOGIN_URL = "/me/signin"

    LOGIN_REDIRECT_URL = "/"

    # Internationalization
    # https://docs.djangoproject.com/en/2.0/topics/i18n/

    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    TESTING = False

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    # Use unpkg.com CDN to serve static assets (overridden in development)

    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    STATIC_URL = values.Value(
        "https://unpkg.com/@stencila/hub@{}/director/static/".format(__version__)
    )

    STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets")]

    # Media files (uploaded by users)
    # https://docs.djangoproject.com/en/2.0/topics/files/

    MEDIA_ROOT = os.path.join(BASE_DIR, "storage")

    MEDIA_URL = "/media/"

    DATA_UPLOAD_MAX_MEMORY_SIZE = values.IntegerValue(5 * 1024 * 1024)

    # Logging
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(levelname)s %(asctime)s %(module)s "
                "%(process)d %(message)s"
            },
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "console"}
        },
        "loggers": {"": {"level": "WARNING", "handlers": ["console"]}},
    }

    ###########################################################################
    # Settings for third-party application in INSTALLED_APPS
    ###########################################################################

    CRISPY_ALLOWED_TEMPLATE_PACKS = ["bulma"]
    CRISPY_TEMPLATE_PACK = "bulma"
    CRISPY_CLASS_CONVERTERS = {
        "checkboxinput": "checkbox",
        "numberinput": "input",
    }

    AVATAR_GRAVATAR_DEFAULT = "identicon"

    SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "SCOPE": [
                "profile",
                "email",
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
            "AUTH_PARAMS": {"access_type": "offline"},
        }
    }

    REST_FRAMEWORK = {
        # Use camel casing for everything (inputs and outputs)
        "DEFAULT_RENDERER_CLASSES": (
            "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        ),
        "DEFAULT_PARSER_CLASSES": (
            "djangorestframework_camel_case.parser.CamelCaseJSONParser",
        ),
        "DEFAULT_PERMISSION_CLASSES": (
            # Default is for API endpoints to require the user to be authenticated
            "rest_framework.permissions.IsAuthenticated",
        ),
        "DEFAULT_AUTHENTICATION_CLASSES": [
            # Default is for token and Django session authentication
            "general.api.authentication.BasicAuthentication",
            "knox.auth.TokenAuthentication",
            "rest_framework.authentication.SessionAuthentication",
        ],
        "EXCEPTION_HANDLER": "general.api.handlers.custom_exception_handler",
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
        "PAGE_SIZE": 50,
        # Use JSON by default when using the test client
        # https://www.django-rest-framework.org/api-guide/testing/#setting-the-default-format
        "TEST_REQUEST_DEFAULT_FORMAT": "json",
    }

    # django-rest-knox settings for API tokens
    # See http://james1345.github.io/django-rest-knox/settings/
    REST_KNOX = {
        # The Prefix to use in the Authorization header
        "AUTH_HEADER_PREFIX": "Token",
        # Automatically refresh the token when it is used
        "AUTO_REFRESH": True,
        # Period until token expires.  None will create tokens that never expire.
        "TOKEN_TTL": datetime.timedelta(days=7),
    }

    SWAGGER_SETTINGS = {
        "SECURITY_DEFINITIONS": {
            "API": {"type": "apiKey", "name": "Authorization", "in": "header"}
        }
    }

    # django-rest-framework-jwt settings for JWT execution session tokens
    # See https://jpadilla.github.io/django-rest-framework-jwt/#additional-settings
    JWT_AUTH = {
        # The Prefix to use in the Authorization header
        "JWT_AUTH_HEADER_PREFIX": "JWT",
        # Period until token expires. Generally recommended to be <15 mins
        "JWT_EXPIRATION_DELTA": datetime.timedelta(minutes=10),
        # Allow token to be refreshed within a given period from initial issuance
        "JWT_ALLOW_REFRESH": True,
        "JWT_REFRESH_EXPIRATION_DELTA": datetime.timedelta(days=1),
    }

    ###########################################################################
    # Settings for integration with external third-party services
    # i.e. Stripe, Sentry etc
    #
    # Many of these are empty, intentionally, and may cause an error, if you
    # go to a particular page that requires them.
    ###########################################################################

    # Use GoogleCloudStorage for uploads
    DEFAULT_FILE_STORAGE = "lib.storage.CustomPublicGoogleCloudStorage"
    GS_PROJECT_ID = values.Value()
    GS_BUCKET_NAME = values.Value()

    # Use SendGrid for emails
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_API_KEY = values.Value()

    # Use Intercom for in app messages
    # For other potential settings see
    # https://django-intercom.readthedocs.io/en/latest/settings.html
    INTERCOM_APPID = values.Value()

    # Use PostHog for product analytics
    POSTHOG_KEY = values.Value()

    # Use Sentry for error reporting
    SENTRY_DSN = values.Value()

    # Use Strip for payments
    # In production, use live mode (overridden in development to use test keys)
    STRIPE_LIVE_MODE = True
    STRIPE_LIVE_PUBLIC_KEY = values.Value("")
    STRIPE_LIVE_SECRET_KEY = values.Value("sk_live_test")
    DJSTRIPE_WEBHOOK_VALIDATION = "retrieve_event"

    ###########################################################################
    # Settings for integration with other Hub services i.e. `broker`, `storage` etc
    ###########################################################################

    # URL to the `broker` service
    BROKER_URL = values.SecretValue(environ_prefix=None)

    # Path to the `storage` service mounted as a
    # local directory. Defaults to the `data` sub-directory
    # of the `storage` service in this repo
    STORAGE_DIR = values.Value(os.path.join(BASE_DIR, "..", "storage", "data"))

    ###########################################################################
    # Settings used internally in the `director`'s own code
    #
    # Some of these may be renamed / removed in the future
    ###########################################################################

    EXECUTION_SERVER_HOST = values.Value()
    EXECUTION_SERVER_PROXY_PATH = values.Value()
    EXECUTION_CLIENT = values.Value("NIXSTER")

    GS_PUBLIC_READABLE_PATHS = ["avatars/*"]
    # these paths will be made publicly readable in the Google Storage bucket after being written to

    # Path to Encoda executable
    # This default path points to the install in the parent directory
    STENCILA_ENCODA_PATH = values.Value(
        os.path.join(
            BASE_DIR, "..", "node_modules", "@stencila", "encoda", "dist", "cli.js"
        )
    )

    STENCILA_CLIENT_USER_AGENT = values.Value("Stencila Hub HTTP Client")

    EXECUTA_HOSTS = values.SingleNestedTupleValue("")
    SPARKLA_PROJECT_ROOT = values.Value("")

    # Rudimentary feature toggle
    FEATURES = {"PROJECT_SESSION_SETTINGS": False}

    # Ensure JWT secret is set
    JWT_SECRET = values.SecretValue()

    @classmethod
    def post_setup(cls):
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=cls.SENTRY_DSN,
            release="hub@{}".format(__version__),
            integrations=[DjangoIntegration()],
            send_default_pii=True,
        )


class Dev(Prod):
    """
    Configuration settings used during development.

    Only override settings that make development easier
    e.g. defaults for secrets that you don't want to
    have to supply in env vars, extra debugging info etc.
    """

    # Ensure debug is always true in development
    DEBUG = True

    # This variable must always be set, even in development.
    SECRET_KEY = "not-a-secret-key"

    # Additional apps only used in development
    INSTALLED_APPS = Prod.INSTALLED_APPS + ["debug_toolbar", "django_extensions"]

    # Required for debug_toolbar
    INTERNAL_IPS = "127.0.0.1"

    # Additional middleware only used in development
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + Prod.MIDDLEWARE

    # Serve from /static, not http://unpkg.com, during development
    STATIC_URL = values.Value("/static/")

    # During development just print emails to console
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # Crispy forms should fail loudly during development
    CRISPY_FAIL_SILENTLY = False

    # Disable intercom. Even though we don't define am `INTERCOM_APPID`
    # during development, without this setting a warning gets emitted
    INTERCOM_DISABLED = True

    # Use Stripe test mode and provide keys for it
    STRIPE_LIVE_MODE = False
    STRIPE_TEST_PUBLIC_KEY = values.Value("")
    STRIPE_TEST_SECRET_KEY = values.Value("sk_test_test")

    # In standalone development, default to using a pseudo, in-memory broker
    BROKER_URL = values.Value("memory://", environ_prefix=None)

    # JWT secret must always be set, even in development.
    JWT_SECRET = "not-a-secret"

    @classmethod
    def post_setup(cls):
        # Allow for username / password API authentication during development
        # only. This is usually disallowed in production (in favour of tokens)
        # but is permitted during development development for convenience.
        cls.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].insert(  # type: ignore
            0, "rest_framework.authentication.BasicAuthentication",
        )


class Test(Prod):
    """
    Configuration settings used during tests.

    These should be as close as possible to production settings.
    So only override settings that are necessary and generally
    only to avoid having to use mock settings in scattered places
    throughout tests.

    Note: for reproducibility these shouldn't be read from env vars; just use strings.
    """

    SECRET_KEY = "not-a-secret-key"

    SECURE_SSL_REDIRECT = False

    BROKER_URL = "memory://"

    JWT_SECRET = "not-a-secret"
