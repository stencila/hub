"""
Module for the `assistant` service.

This is a standard Django-Celery integration setup.
See `make run-assistant` for running during development with the
necessary environment variables.
See `assistant.Dockerfile` for running in production.

See
 - https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
 - https://django-configurations.readthedocs.io/en/stable/cookbook/#celery
"""

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manager.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Prod")

import configurations  # noqa

configurations.setup()

app = Celery("manager", broker=os.environ["BROKER_URL"])

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# Namespace='CELERY' means all celery-related configuration keys
# should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
