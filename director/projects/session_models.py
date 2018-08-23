import enum
import time

import jwt
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
import requests


class SessionStatus(enum.Enum):
    UNKNOWN = 'Unknown'
    NOT_STARTED = 'Not Started'
    RUNNING = 'Running'
    STOPPED = 'Stopped'


class Session(models.Model):
    """
    An execution Session
    """
    project = models.ForeignKey(
        'Project',
        null=False,
        on_delete=models.PROTECT,  # Don't want to delete references if the container is running and we need control still
        related_name='sessions',
        help_text='The Project that this Session belongs to.'
    )

    url = models.URLField(
        help_text='URL for API access to administrate this Session'
    )

    started = models.DateTimeField(
        null=True,
        help_text='DateTime this Session was started'
    )

    stopped = models.DateTimeField(
        null=True,
        help_text='DateTime this Session was stopped (or that we detected it had stopped)'
    )

    last_check = models.DateTimeField(
        null=True,
        help_text='The last time the status of this Session was checked'
    )

    @staticmethod
    def create(project, environ):
        """
        Create a session for a project on a remote Stencila execution Host (usually
        an instance of `stencila/cloud` but could even be a user's local machine)
        """
        # TODO check the total number and number of concurrent sessions for project

        # TODO: This will eventually come from the `SessionParameters` for this project
        host_url = settings.NATIVE_HOST_URL

        # Create a JWT token for the host
        jwt_secret = settings.JWT_SECRET  # TODO: This will eventually come from the settings for the remote host
        jwt_payload = dict(iat=time.time())
        jwt_token = jwt.encode(jwt_payload, jwt_secret, algorithm='HS256').decode("utf-8")

        # TODO: add `SessionParameters` to the POST body (currently they won't do anything anyway)
        response = requests.post(host_url + '/sessions/' + environ, headers={
            'Authorization': 'Bearer ' + jwt_token
        })
        response.raise_for_status()

        try:
            result = response.json()
        except Exception as exc:
            raise Exception('Error parsing body: ' + response.text)

        url = result.get('url')
        if url is None:
            path = result.get('path')
            assert path is not None
            url = host_url + path

        # TODO set the started time
        # TODO should we record some of the request
        # headers e.g. `REMOTE_ADDR`, `HTTP_USER_AGENT`, `HTTP_REFERER` for analytics?
        return Session.objects.create(
            project=project,
            url=url
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
    owner = models.ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=models.SET_NULL,
        related_name='session_templates',
        help_text='User who owns the SessionParameters'
    )

    is_system = models.BooleanField(
        default=False,
        help_text='If True, this SessionParameters can be used by any user'
    )

    display_order = models.IntegerField(
        null=False,
        blank=True,
        default=0,
        help_text="The order this SessionParameter should be displayed in list/tables"
    )

    name = models.TextField(
        null=False,
        blank=False
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text='Optional long description about the SessionParameters'
    )

    memory = models.FloatField(
        default=1,
        null=False,
        blank=False,
        help_text='Gigabytes (GB) of memory allocated'
    )

    cpu = models.FloatField(
        default=1,
        null=False,
        blank=False,
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
        null=False,
        blank=False,
        help_text='Minutes of inactivity before the session is terminated'
    )

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse('sessionparameters_update', args=[self.pk])
