"""
Django settings for manager service.

Uses `django-configurations` to define settings
for different environments.
See https://github.com/jazzband/django-configurations.
"""

import datetime
import os
from typing import Dict, List

import djangocodemirror.settings as dcm_settings
from configurations import Configuration, values

from manager.version import __version__

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Prod(Configuration):
    """
    Configuration settings used in production.

    This should include all the settings needed in production.
    To keep `Dev` and `Test` settings as close as possible to those
    in production we use `Prod` as a base and only override as needed.
    """

    ###########################################################################
    # Core Django settings
    #
    # For a complete list see https://docs.djangoproject.com/en/3.0/ref/settings/
    ###########################################################################

    # A boolean that turns on/off debug mode.
    # Ensure debug is always false in production (overridden in development)
    DEBUG = False

    # A secret key for a particular Django installation.
    # Use `SecretValue` to require that a `DJANGO_SECRET_KEY` environment variable
    # is set during production
    SECRET_KEY = values.SecretValue()

    # A list of strings representing the host/domain names that this Django site can serve.
    # In production, use wildcard because load balancers
    # perform health checks without host specific Host header value
    ALLOWED_HOSTS = ["*"]

    # Enforce HTTPS
    # Allow override to be able to test other prod settings during development
    # in a Docker container (ie. locally not behind a HTTPS load balancer)
    # See `make run-prod`
    SECURE_SSL_REDIRECT = values.BooleanValue(True)

    # If a URL path matches a regular expression in this list, the request will not be
    # redirected to HTTPS.
    # Do not redirect URLs used by other Stencila Hub services and by load balancer
    # health checks (which all operate over the private network)
    SECURE_REDIRECT_EXEMPT = [
        # Used by `overseer` service
        r"^api/workers/",
        r"^api/jobs/",
        # Used by `monitor` service
        r"^api/metrics/",
        # Used by health checks
        r"^api/status/?$",
        r"^/?$",
    ]

    # A tuple representing a HTTP header/value combination that signifies a request is secure.
    # This controls the behavior of the request object’s is_secure() method.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # A list of strings designating all applications that are enabled in this Django installation.
    INSTALLED_APPS = [
        # Django contrib apps
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django.contrib.humanize",
        # Third party apps
        "allauth",
        "allauth.account",
        "allauth.socialaccount.providers.github",
        "allauth.socialaccount.providers.google",
        "allauth.socialaccount.providers.orcid",
        "allauth.socialaccount.providers.twitter",
        "allauth.socialaccount",
        "corsheaders",
        "django_celery_beat",
        "django_intercom",
        "django_prometheus",
        "djangocodemirror",
        "drf_yasg",
        "imagefield",
        "invitations",
        "knox",
        "polymorphic",
        "rest_framework",
        "waffle",
        # Add this for our template tags
        "manager",
        # Our apps
        # Uses dotted paths to AppConfig subclasses as
        # recommended in https://docs.djangoproject.com/en/3.0/ref/applications/#configuring-applications
        "accounts.apps.AccountsConfig",
        "jobs.apps.JobsConfig",
        "projects.apps.ProjectsConfig",
        "users.apps.UsersConfig",
    ]

    # A list of middleware to use.
    MIDDLEWARE = [
        # From https://pypi.org/project/django-cors-headers/: "CorsMiddleware should be placed as high as
        # possible, especially before any middleware that can generate responses such as Django’s
        # CommonMiddleware or Whitenoise’s WhiteNoiseMiddleware"
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.security.SecurityMiddleware",
        # Whitenoise must be above all other middleware apart from Django’s SecurityMiddleware
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django_prometheus.middleware.PrometheusBeforeMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "waffle.middleware.WaffleMiddleware",
        "django_prometheus.middleware.PrometheusAfterMiddleware",
        "manager.middleware.method_override",
        "manager.middleware.session_storage",
        # Must be last one to capture the exception
        "manager.middleware.CustomExceptionsMiddleware",
    ]

    # A string representing the full Python import path to your root URLconf
    ROOT_URLCONF = "manager.urls"

    # A list containing the settings for all template engines to be used with Django
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [
                os.path.join(BASE_DIR, "manager", "templates"),
                # Ensure that allauth templates are overridden by ours
                os.path.join(BASE_DIR, "users", "templates"),
            ],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "manager.context_processors.versions",
                    "manager.context_processors.settings",
                ],
            },
        },
    ]

    # The full Python path of the WSGI application object that Django’s built-in servers (e.g. runserver) will use
    WSGI_APPLICATION = "manager.wsgi.application"

    # The ID, as an integer, of the current site in the django_site database table
    # Required because `django.contrib.sites` is required by `allauth`
    SITE_ID = 1

    # Database defaults to `dev.sqlite3` but can be set using `DATABASE_URL` env var
    # Note that the three leading slashes are *intentional*
    # See https://github.com/kennethreitz/dj-database-url#url-schema
    DATABASES = values.DatabaseURLValue(
        "sqlite:///{}".format(os.path.join(BASE_DIR, "dev.sqlite3"))
    )

    # Default email address to use for various automated correspondence from the site manager(s)
    DEFAULT_FROM_EMAIL = values.Value("hello@stenci.la")

    # Store session data in signed cookies (alternatives include DB or cache)
    SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
    # Extend age of cookie from default 2 weeks to avoid users having to
    # sign in again and potentially use a different authentication method.
    SESSION_COOKIE_AGE = 31536000  # A year in seconds.
    # Allow session cookies to be sent from other domains.
    # CORS restrictions elsewhere limit this to ACCOUNTS_DOMAIN
    # Note: The 'None' below is intentionally a string and not a `None` value.
    # See https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SESSION_COOKIE_SAMESITE
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True

    # Authentication
    # https://docs.djangoproject.com/en/3.0/ref/settings/#auth

    AUTHENTICATION_BACKENDS = (
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    )

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    # URL to redirect users for authentication required views
    # Note: the trailing / is important to avoid a redirect loop.
    LOGIN_URL = "/me/signin/"

    LOGIN_REDIRECT_URL = "/"

    # Internationalization
    # https://docs.djangoproject.com/en/3.0/topics/i18n/

    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/3.0/howto/static-files/

    STATIC_URL = "/static/"

    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    # Caching
    # See https://docs.djangoproject.com/en/3.0/topics/cache

    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

    # Logging
    # See https://docs.djangoproject.com/en/3.0/topics/logging/

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

    # django-cors-headers
    # See https://github.com/adamchainz/django-cors-headers#configuration
    # This gets populated, based on the ACCOUNTS_SUBDOMAIN setting in post_setup
    CORS_ALLOWED_ORIGIN_REGEXES: List[str] = [
        # Allow cross-origin requests from Stencila's GoogleDocs Add-on
        r"^https://n-zoqnmwqnnhslxffeq3hh6ne46wicurqczwe4csa-0lu-script.googleusercontent.com?$"
    ]
    # This allows credentials to be sent in cross-origin requests
    CORS_ALLOW_CREDENTIALS = True

    # django-allauth settings
    # See https://django-allauth.readthedocs.io/en/latest/configuration.html

    ACCOUNT_EMAIL_REQUIRED = True

    ACCOUNT_ADAPTER = "invitations.models.InvitationsAdapter"

    SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "SCOPE": [
                "profile",
                "email",
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
            # Set to offline in order to receive a refresh token on first login and
            # on reauthentication requests. See https://stackoverflow.com/a/42570423/4625911
            "AUTH_PARAMS": {"access_type": "offline"},
        }
    }

    SOCIALACCOUNT_ADAPTER = "users.socialaccount.adapter.SocialAccountAdapter"

    # django-imagefield settings
    # See https://django-imagefield.readthedocs.io/en/latest/
    #
    # It seems necessary to define these here to avoid errors on initial
    # bootstapping when including the `manager.assistant` module. However, we do not use
    # this `IMAGEFIELD_FORMATS` settins and instead set these formats on the `ImageFields`
    # themselves

    IMAGEFIELD_FORMATS: Dict = {}
    IMAGEFIELD_AUTOGENERATE = True

    # django-invitations settings
    # See https://github.com/bee-keeper/django-invitations#additional-configuration

    INVITATIONS_INVITATION_EXPIRY = 14
    INVITATIONS_GONE_ON_ACCEPT_ERROR = False
    INVITATIONS_SIGNUP_REDIRECT = "ui-users-signup"
    INVITATIONS_LOGIN_REDIRECT = "ui-users-signin"
    INVITATIONS_ACCEPT_INVITE_AFTER_SIGNUP = True
    INVITATIONS_ADAPTER = ACCOUNT_ADAPTER
    INVITATIONS_EMAIL_MAX_LENGTH = 1024
    INVITATIONS_EMAIL_SUBJECT_PREFIX = "Invitation to Stencila"
    INVITATIONS_INVITATION_MODEL = "users.Invite"

    # django-waffle settings
    # See https://waffle.readthedocs.io/en/stable/starting/configuring.html

    WAFFLE_FLAG_MODEL = "users.Flag"

    # django-rest-framework settings

    # Rate limits for API. These defaults are the similar to Github but
    # are slightly higher for anonymous users (IP based)
    DEFAULT_THROTTLE_RATE_ANON = values.Value("100/hour")
    DEFAULT_THROTTLE_RATE_USER = values.Value("5000/hour")

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
            "manager.api.authentication.BasicAuthentication",
            "knox.auth.TokenAuthentication",
            "rest_framework.authentication.SessionAuthentication",
        ],
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ],
        "REST_FRAMEWORK": {
            # These rates only apply to `/api` endpoints. They
            # do not include "pseudo-requests" made via view sets
            # in UI views, but will include HTMX-initiated async API
            # requests made in response to user actions (including search).
            # Thus they can be set quite low for anonymous
            # users without affecting anon user page views.
            # A `429 Too Many Requests` response is returned when rate
            # limits are exceeded.
            # These values are populated in the setup method below.
            "anon": None,
            "user": None,
        },
        "EXCEPTION_HANDLER": "manager.api.handlers.custom_exception_handler",
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
        "PAGE_SIZE": 50,
        # Use JSON by default when using the test client
        # https://www.django-rest-framework.org/api-guide/testing/#setting-the-default-format
        "TEST_REQUEST_DEFAULT_FORMAT": "json",
    }

    # django-rest-knox settings
    # See http://james1345.github.io/django-rest-knox/settings/

    REST_KNOX = {
        # The Prefix to use in the Authorization header
        "AUTH_HEADER_PREFIX": "Token",
        # Automatically refresh the token when it is used
        "AUTO_REFRESH": True,
        # Period until token expires.  None will create tokens that never expire.
        "TOKEN_TTL": datetime.timedelta(days=7),
    }

    # drf-yasg settings
    # See https://drf-yasg.readthedocs.io/en/stable/settings.html

    SWAGGER_SETTINGS = {
        "SECURITY_DEFINITIONS": {
            "Token": {"type": "apiKey", "name": "Authorization", "in": "header"}
        }
    }

    # djangocodemirror settings
    # See https://djangocodemirror.readthedocs.io/en/latest/settings.html
    CODEMIRROR_FIELD_INIT_JS = dcm_settings.CODEMIRROR_FIELD_INIT_JS
    CODEMIRROR_SETTINGS = dcm_settings.CODEMIRROR_SETTINGS
    CODEMIRROR_BASE_JS = dcm_settings.CODEMIRROR_BASE_JS
    CODEMIRROR_BASE_CSS = dcm_settings.CODEMIRROR_BASE_CSS
    CODEMIRROR_THEMES = dcm_settings.CODEMIRROR_THEMES
    CODEMIRROR_MODES = dcm_settings.CODEMIRROR_MODES
    CODEMIRROR_JS_ASSET_TAG = dcm_settings.CODEMIRROR_JS_ASSET_TAG
    CODEMIRROR_CSS_ASSET_TAG = dcm_settings.CODEMIRROR_CSS_ASSET_TAG
    CODEMIRROR_BUNDLE_CSS_NAME = dcm_settings.CODEMIRROR_BUNDLE_CSS_NAME
    CODEMIRROR_BUNDLE_JS_NAME = dcm_settings.CODEMIRROR_BUNDLE_JS_NAME

    ###########################################################################
    # Settings for integration with external third-party services
    # i.e. Stripe, Sentry etc
    #
    # Many of these are intentionally empty. This may cause an error if you
    # go to a particular page that requires them.
    ###########################################################################

    # SendGrid settings

    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_API_KEY = values.Value()

    # Intercom settings
    # For other potential settings see
    # https://django-intercom.readthedocs.io/en/latest/settings.html

    INTERCOM_APPID = values.Value()
    # Token to use the Intercom API. See
    # https://developers.intercom.com/building-apps/docs/authentication-types#section-access-tokens
    INTERCOM_ACCESS_TOKEN = values.Value()

    # UserFlow settings

    USERFLOW_KEY = values.Value()

    # PostHog settings

    POSTHOG_KEY = values.Value()

    # Sentry settings

    SENTRY_DSN = values.Value()

    # Stripe settings
    # In production, use live mode (overridden in development to use test keys)

    STRIPE_LIVE_MODE = True
    STRIPE_LIVE_PUBLIC_KEY = values.Value("")
    STRIPE_LIVE_SECRET_KEY = values.Value("sk_live_test")
    DJSTRIPE_WEBHOOK_VALIDATION = "retrieve_event"

    ###########################################################################
    # Settings for integration with other Hub services i.e. `broker`, `storage` etc
    ###########################################################################

    # URL of the `broker` service
    BROKER_URL = values.SecretValue(environ_prefix=None)

    # URL of the `cache` service
    CACHE_URL = values.SecretValue(environ_prefix=None)

    ###########################################################################
    # Settings used internally in the `manager`'s own code
    #
    # Some of these may be renamed / removed in the future
    ###########################################################################

    # An environment name e.g. prod, staging, test used for
    # exception reporting / filtering
    DEPLOYMENT_ENVIRONMENT = values.Value(environ_prefix=None)

    # Directories for storage e.g. `uploads`, `working`, `snapshots`
    # (see `storage.py`).
    # In development and testing the local filesystem is used.
    # In production, storage is provided by other, possibly external,
    # services e.g. S3, or NFS (but may be mounted into these locations)
    MEDIA_ROOT = values.Value()
    UPLOADS_ROOT = values.Value()
    WORKING_ROOT = values.Value()
    SNAPSHOTS_ROOT = values.Value()

    # Allow for username / password API authentication
    # This is usually disallowed in production (in favour of tokens)
    # but is permitted during development for convenience.
    API_BASIC_AUTH = values.BooleanValue(False)

    # Allow for username / password authentication for non-API views
    # This is usually disallowed in production but is permitted
    # during development for ease of testing.
    UI_BASIC_AUTH = values.BooleanValue(False)

    # The primary domain from which the Hub is served.
    # Used to redirect from "account.stencila.io"
    # (i.e. no project specified) to "hub.stenci.la/account"
    PRIMARY_DOMAIN = "hub.stenci.la"

    # The domain from which account subdomains are served
    ACCOUNTS_DOMAIN = "stencila.io"

    # Use local URLs for jobs
    # If this is True the URLs of session jobs are local
    # not global. This is useful during development as
    # it avoids the need for the `router` service to reverse
    # proxy Websocket connections.
    JOB_URLS_LOCAL = values.BooleanValue(False)

    # A list of job methods restricted to staff members
    JOB_METHODS_STAFF_ONLY: List[str] = []

    @classmethod
    def post_setup(cls):
        """Do additional configuration after initial setup."""
        # Default for environment name is the name of the settings class
        if not cls.DEPLOYMENT_ENVIRONMENT:
            cls.DEPLOYMENT_ENVIRONMENT = cls.__name__.lower()

        # Add UI Basic auth if allowed
        if cls.UI_BASIC_AUTH:
            cls.MIDDLEWARE += ("manager.middleware.basic_auth",)

        # Set default API throttling rates
        cls.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
            "anon": cls.DEFAULT_THROTTLE_RATE_ANON,
            "user": cls.DEFAULT_THROTTLE_RATE_USER,
        }

        # Allow requests from any account subdomains
        # Yes, it is important to append to the existing list, rather
        # than replace it, even if it is empty.
        cls.CORS_ALLOWED_ORIGIN_REGEXES += [
            "^https?://[a-z0-9-]+\\.{0}$".format(
                cls.ACCOUNTS_DOMAIN.replace(".", "\\.")
            )
        ]

        #  Setup sentry if a DSN is provided
        if cls.SENTRY_DSN:
            import logging

            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration

            sentry_sdk.init(
                dsn=cls.SENTRY_DSN,
                release="hub@{}".format(__version__),
                integrations=[
                    DjangoIntegration(),
                    LoggingIntegration(
                        level=logging.INFO,  # Capture info and above as breadcrumbs
                        event_level=logging.WARNING,  # Send warnings and errors as events
                    ),
                ],
                send_default_pii=True,
                environment=cls.DEPLOYMENT_ENVIRONMENT,
            )


class Staging(Prod):
    """
    Configuration for staging environment.
    """

    DEPLOYMENT_ENVIRONMENT = "staging"

    PRIMARY_DOMAIN = "hub-test.stenci.la"

    ACCOUNTS_DOMAIN = "account-test.stenci.la"


class Local(Prod):
    """
    A base configration that uses local storage.
    """

    STORAGE_ROOT = os.getenv(
        "STORAGE_ROOT", os.path.join(BASE_DIR, "..", "storage", "data")
    )
    MEDIA_ROOT = values.Value(os.path.join(STORAGE_ROOT, "media"))
    UPLOADS_ROOT = values.Value(os.path.join(STORAGE_ROOT, "uploads"))
    WORKING_ROOT = values.Value(os.path.join(STORAGE_ROOT, "working"))
    SNAPSHOTS_ROOT = values.Value(os.path.join(STORAGE_ROOT, "snapshots"))


class Dev(Local):
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

    # Allow session cookie to be sent over HTTP
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    # Required for debug_toolbar
    INTERNAL_IPS = "127.0.0.1"

    # Additional middleware only used in development
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + Prod.MIDDLEWARE

    # Add the request history panel to the debug_toolbar
    DEBUG_TOOLBAR_PANELS = [
        "ddt_request_history.panels.request_history.RequestHistoryPanel",  # Here it is
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]

    # During development just print emails to console
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # Disable intercom. Even though we don't define am `INTERCOM_APPID`
    # during development, without this setting a warning gets emitted
    INTERCOM_DISABLED = True

    # Use Stripe test mode and provide keys for it
    STRIPE_LIVE_MODE = False
    STRIPE_TEST_PUBLIC_KEY = values.Value("")
    STRIPE_TEST_SECRET_KEY = values.Value("sk_test_test")

    # In standalone development, default to using a pseudo, in-memory broker
    BROKER_URL = values.Value("memory://", environ_prefix=None)

    # For easier testing allow username/password Basic auth for API
    API_BASIC_AUTH = True

    # For browser screenshotting allow username/password
    # Basic auth on non-API views
    UI_BASIC_AUTH = True

    # Use localhost as the primary domain
    PRIMARY_DOMAIN = "127.0.0.1:8000"

    # For testing of CORS headers locally add an entry in /etc/hosts for an account
    # e.g. `127.0.0.1 admin.stencila.io`
    ACCOUNTS_DOMAIN = "stencila.io:9000"

    # Use local URLs to more easily tests connections to jobs
    JOB_URLS_LOCAL = True


class Test(Local):
    """
    Configuration settings used during tests.

    These should be as close as possible to production settings.
    So keep overrides to a minimum and generally only to avoid having to use
    mock settings in scattered places throughout tests.

    Note: for reproducibility these shouldn't be read from env vars; just use strings.
    """

    # This variable must always be set, even in tests.
    SECRET_KEY = "not-a-secret-key"

    # Obviously redirecting to HTTPS during tests is a Bad Thing To Do
    SECURE_SSL_REDIRECT = False

    # During testing, default to using a pseudo, in-memory broker
    BROKER_URL = "memory://"

    # During testing this value needs to be set but is not used
    CACHE_URL = ""
