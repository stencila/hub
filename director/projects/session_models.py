"""
Models implementing Stencila Hub Sessions.

Whenever a user is accessing a project and running the code in the interactive cells, Stencila Hub creates a Session
which connects to a Stencila Cloud instance which provides the environment for running the code. Each Session has
parameters related to computational resources.

Each Project can have a number of Sessions related to it. These Sessions are grouped in a Session Group.
"""

import enum
from datetime import timedelta

from django.db import models
from django.db.models import QuerySet, Q
from django.urls import reverse
from django.utils import timezone

SESSION_POLL_TIMEOUT = 60  # default for number of seconds since update that Session info is out of date
SESSION_QUEUE_CHECK_TIMEOUT = 120  # remove a `SessionQueue` if it hasn't been checked for this many seconds


class SessionStatus(enum.Enum):
    UNKNOWN = 'Unknown'
    NOT_STARTED = 'Not Started'
    RUNNING = 'Running'
    STOPPED = 'Stopped'


class SessionManager(models.Manager):
    def filter_project_and_status(self, project: 'Project', status: SessionStatus) -> QuerySet:
        """
        Helper method for retrieving `Session`s with a particular `SessionStatus`, since the `status` attribute is
        dynamically updated based on when the `Session` was polled, stopped or started.
        """
        filter_kwargs = {'project': project}

        if status == SessionStatus.UNKNOWN:
            filter_kwargs['last_check__isnull'] = True
        elif status == SessionStatus.NOT_STARTED:
            filter_kwargs['last_check__isnull'] = False
            filter_kwargs['started'] = None
        elif status == SessionStatus.RUNNING:
            filter_kwargs['last_check__isnull'] = False
            filter_kwargs['started__lt'] = timezone.now()
            filter_kwargs['stopped__isnull'] = True
        elif status == SessionStatus.STOPPED:
            filter_kwargs['last_check__isnull'] = False
            filter_kwargs['stopped__lt'] = timezone.now()

        return super().get_queryset().filter(**filter_kwargs)

    def filter_stale_status(self) -> QuerySet:
        """
        Filter `Session`s to those that are "stale": their `last_check` is null (never checked) or more than
        `SESSION_POLL_TIMEOUT` seconds ago, and are not stopped (`stopped` is null).

        Generally the methods that call this should add extra filters to this return value, e.g:
        `Session.objects.filter_stale_status().filter(project=project)`
        """
        last_check_filter = Q(last_check=None) | Q(
            last_check__lt=timezone.now() - timedelta(seconds=SESSION_POLL_TIMEOUT))

        return super().get_queryset().filter(last_check_filter, stopped=None)


class Session(models.Model):
    """
    An execution Session
    """
    objects = SessionManager()

    project = models.ForeignKey(
        'Project',
        null=False,
        on_delete=models.PROTECT,
        # Don't want to delete references if the container is running and we need control still
        related_name='sessions',
        db_index=True,
        help_text='The Project that this Session belongs to.'
    )

    url = models.URLField(
        help_text='URL for API access to administrate this Session',
        db_index=True
    )

    started = models.DateTimeField(
        null=True,
        blank=True,
        help_text='DateTime this Session was started.'
    )

    stopped = models.DateTimeField(
        null=True,
        blank=True,
        help_text='DateTime this Session was stopped (or that we detected it had stopped).'
    )

    last_check = models.DateTimeField(
        null=True,
        blank=True,
        help_text='The last time the status of this Session was checked'
    )

    @property
    def status(self) -> SessionStatus:
        if self.last_check is None:
            return SessionStatus.UNKNOWN

        if self.stopped is not None and self.stopped <= timezone.now():
            return SessionStatus.STOPPED

        if self.started is not None and self.started <= timezone.now():
            return SessionStatus.RUNNING

        return SessionStatus.NOT_STARTED


class SessionParameters(models.Model):
    """
    Defines the parameters for new Sessions created in a Project
    """

    name = models.TextField(
        null=True,
        blank=True,
        help_text='Names for the set of session parameters (optional). This can be used if you want to save a pre-set '
                  'Session Parameters'
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text='Optional long description about the SessionParameters'
    )

    memory = models.FloatField(
        default=1,
        null=True,
        blank=True,
        help_text='Gigabytes (GB) of memory allocated'
    )

    cpu = models.FloatField(
        default=1,
        null=True,
        blank=True,
        help_text='CPU shares (out of 100 per CPU) allocated'
    )

    network = models.FloatField(
        null=True,
        blank=True,
        help_text='Gigabytes (GB) of network transfer allocated. null = unlimited'
    )

    lifetime = models.IntegerField(
        null=True,
        blank=True,
        help_text='Minutes before the session is terminated. null = unlimited'
    )

    timeout = models.IntegerField(
        default=60,
        null=True,
        blank=True,
        help_text='Minutes of inactivity before the session is terminated'
    )

    def __str__(self) -> str:
        return self.name if self.name else 'SessionParameters #{}'.format(self.id)

    def get_absolute_url(self):
        return reverse('sessionparameters_update', args=[self.pk])

    def serialize(self) -> dict:
        return {
            "pk": self.pk,
            "name": self.name,
            "description": self.description,
            "memory": self.memory,
            "cpu": self.cpu,
            "network": self.network,
            "lifetime": self.lifetime,
            "timeout": self.timeout
        }


class SessionRequest(models.Model):
    """
    A request to queue the creation of  a `Session` for when the `Project` already has the maximum number of sessions
    running (`sessions_concurrent`).
    """

    project = models.ForeignKey(
        'Project',
        null=False,
        on_delete=models.CASCADE,
        related_name='session_requests',
        db_index=True,
        help_text='The project this request is for'
    )

    created = models.DateTimeField(
        null=False,
        auto_now_add=True,
        help_text='The date and time the request for a session was created.'
    )

    last_check = models.DateTimeField(
        null=False,
        auto_now=True,
        help_text='The last time that a client queried against this request'
    )

    environ = models.TextField(
        null=False,
        help_text='The environment in which to create the Session'
    )
