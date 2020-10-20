# Ensure the `assistant` service's Celery `app` is always imported when
# Django starts so that the `shared_task` decorator uses it.
#
# See https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

from .assistant import app as celery_app

__all__ = ("celery_app",)
