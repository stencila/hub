"""
Minimal settings module necessary to run `django_celery_beat`.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import secrets

import dj_database_url

INSTALLED_APPS = ["django_celery_beat"]

# Read and parse the DATABASE_URL env var.
DATABASES = {"default": dj_database_url.config()}

# Time zone awareness needs to be the same as in the database
DJANGO_CELERY_BEAT_TZ_AWARE = False

# Although not used, and therefore not strictly necessary,
# Django complains if this is empty. We use a random
# token just in case it is used.
SECRET_KEY = secrets.token_hex(32)
