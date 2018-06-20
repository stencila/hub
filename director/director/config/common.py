import os
from os.path import dirname
from configurations import Configuration, values

DIRECTOR_DIR = dirname(dirname(dirname(__file__)))


class Common(Configuration):

    DEBUG = values.BooleanValue(True)

    SECRET_KEY = values.SecretValue()

    ADMINS = (
        ('Nokome Bentley', 'nokome@stenci.la'),
    )

    ALLOWED_HOSTS = ['*']

    INSTALLED_APPS = [
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
        # adding the credentials provided by the provider
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.linkedin_oauth2',
        'allauth.socialaccount.providers.orcid',
        'allauth.socialaccount.providers.twitter',
        'storages',

        'crispy_forms',
        'crispy_forms_bulma',

        'director',
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

    ROOT_URLCONF = 'director.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(DIRECTOR_DIR, 'templates')
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

    WSGI_APPLICATION = 'director.wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/2.0/ref/settings/#databases
    # Note that the three leading slashes are *intentional*
    # See https://github.com/kennethreitz/dj-database-url#url-schema
    DATABASES = values.DatabaseURLValue(
        'sqlite:///%s/db.sqlite3' % DIRECTOR_DIR,
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
    STATIC_URL = values.Value('/static/')
    STATICFILES_DIRS = [
        os.path.join(DIRECTOR_DIR, 'client')
    ]
    STATIC_ROOT = os.path.join(DIRECTOR_DIR, 'static')

    SITE_ID = 1

    LOGIN_URL = '/me/signin/'
    LOGIN_REDIRECT_URL = '/'

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
        'director.auth_backends.GuestAuthBackend',
    )

    ACCOUNT_SESSION_REMEMBER = True  # Always remember the user
    ACCOUNT_SESSION_COOKIE_AGE = 31536000  # Sessions to last up to a year 60*60*24*365
    SOCIALACCOUNT_ADAPTER = 'director.allauth_adapter.SocialAccountAdapter'
    ACCOUNT_EMAIL_REQUIRED = True
    SOCIALACCOUNT_QUERY_EMAIL = True
    SOCIALACCOUNT_PROVIDERS = {
        'facebook': {
            'SCOPE': ['email'],
            'METHOD': 'oauth2',
        },
        'github': {
            'SCOPE': ['user:email']
        },
        'google': {
            'SCOPE': ['profile', 'email'],
            'AUTH_PARAMS': {'access_type': 'online'}
        },
        'linkedin': {
            'SCOPE': ['r_fullprofile', 'r_emailaddress'],
            'PROFILE_FIELDS': [
                'id',
                'first-name',
                'last-name',
                'email-address',
                'picture-url',
                'public-profile-url'
            ]
        },
        'orcid': {
        },
        'twitter': {
        },
    }

    CRISPY_ALLOWED_TEMPLATE_PACKS = ('bulma',)
    CRISPY_TEMPLATE_PACK = 'bulma'

    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_PROJECT_ID = values.Value()
    GS_BUCKET_NAME = values.Value()

    JWT_SECRET = values.SecretValue()

    STORAGE_DIR = values.Value(os.path.join(DIRECTOR_DIR, 'storage'))
    SECRETS_DIR = values.Value(os.path.join(DIRECTOR_DIR, 'secrets'))

    UNCONVERTIBLE_FILE_TYPES = []
    CONVERT_MAX_SIZE = 10485760
