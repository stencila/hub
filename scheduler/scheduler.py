"""
Stencila Hub Scheduler.

A Celery app for running `celery beat` to queue periodic tasks.
See https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html.

The definition of the periodic tasks is done in within the `director`
database using django_celery_beat.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django

django.setup()

from celery import Celery
from django_celery_beat.schedulers import DatabaseScheduler

app = Celery(
    broker=os.environ.get("BROKER_URL"), scheduler=DatabaseScheduler, loglevel="INFO"
)
