import os
import sys

from os.path import join, dirname
from django.conf.locale.en import formats as en_formats
from configurations import Configuration, values

BASE_DIR = dirname(dirname(dirname(__file__)))


class Common(Configuration):
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
        #   - add a SocialApp instance (/admin/socialaccount/socialapp/add/) adding the credentials provided by the provider
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.linkedin',
        'allauth.socialaccount.providers.orcid',
        'allauth.socialaccount.providers.twitter',

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

    WSGI_APPLICATION = 'director.wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/2.0/ref/settings/#databases

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

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
        os.path.join(BASE_DIR, 'client')
    ]
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

    SITE_ID = 1

    LOGIN_URL = '/me/signin/'
    LOGIN_REDIRECT_URL = '/'

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
        'director.auth_backends.GuestAuthBackend',
    )

    ACCOUNT_SESSION_REMEMBER = True # Always remember the user
    ACCOUNT_SESSION_COOKIE_AGE = 31536000 # Sessions to last up to a year 60*60*24*365
    SOCIALACCOUNT_ADAPTER = 'director.allauth_adapter.SocialAccountAdapter'
    ACCOUNT_EMAIL_REQUIRED = True
    SOCIALACCOUNT_QUERY_EMAIL = True
    SOCIALACCOUNT_PROVIDERS = {
        'facebook': {
            # See https://github.com/pennersr/django-allauth#facebook
            # Manage the app at http://developers.facebook.com logged in as user `stencila`
            # Callback URL must be HTTP
            'SCOPE': ['email'],
            'METHOD': 'oauth2',
        },
        'github': {
            # See http://developer.github.com/v3/oauth/#scopes for list of scopes available
            # At the time of writing it was not clear if scopes are implemented in allauth for Github
            # see https://github.com/pennersr/django-allauth/issues/369
            # Manage the app at https://github.com/organizations/stencila/settings/applications/74505
            # Callback URL must be HTTP
            'SCOPE': ['user:email']
        },
        'google': {
            # Manage the app at
            #   https://code.google.com/apis/console/
            #   https://cloud.google.com/console/project/582496091484/apiui/credential
            #   https://cloud.google.com/console/project/582496091484/apiui/consent
            'SCOPE': ['profile', 'email'],
            'AUTH_PARAMS': {'access_type': 'online'}
        },
        'linkedin': {
            # Manage the app at
            #  https://www.linkedin.com/developer/apps/3129843/auth
            # logged in as a user with access rights to the app
            # The scopes are listed on the above page
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
            # Manage the app at https://orcid.org/developer-tools logged in as 0000-0003-1608-7967 (Nokome Bentley)
        },
        'twitter': {
            # Manage the app at https://dev.twitter.com/apps/5640979/show logged in as user `stencila`
        },
    }

    CRISPY_ALLOWED_TEMPLATE_PACKS = ('bulma',)
    CRISPY_TEMPLATE_PACK = 'bulma'

