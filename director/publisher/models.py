import datetime
import enum
import hashlib
import secrets

from django.db.models import (Model, ForeignKey, DateTimeField, SET_NULL, TextField, IntegerField, URLField, FloatField,
                              PROTECT)
from django.utils import timezone

TOKEN_HASH_FUNCTION = hashlib.sha256
SESSION_GROUP_KEY_LENGTH = 32
TRUNCATED_TOKEN_SHOW_CHARACTERS = 8


def generate_session_group_token(session_group: 'SessionGroup') -> str:
    """Generate a unique token for a SessionGroup based on its creator, creation date and a random string."""
    user_id = session_group.owner.id if session_group.owner else None
    created = session_group.created or datetime.datetime.now()
    return TOKEN_HASH_FUNCTION("{}{}{}".format(user_id, created, secrets.token_hex()).encode("utf8")).hexdigest()


def generate_session_group_key() -> str:
    """Generate a random key for a SessionGroup."""
    return secrets.token_hex(SESSION_GROUP_KEY_LENGTH)


class SessionGroup(Model):
    """
    Contains references to a group of Sessions that can be created, and sets limits to the number of sessions that can
    be created and what resources they have (with a SessionTemplate)
    """
    owner = ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=SET_NULL,
        related_name='session_groups',
        help_text='User who owns the SessionGroup'
    )

    created = DateTimeField(
        auto_now_add=True,
        help_text='When the SessionGroup was created'
    )

    token = TextField(
        unique=True,
        help_text='A token to publicly identify the SessionGroup (in URLs etc)'
    )

    key = TextField(
        null=True,
        blank=True,
        help_text='Key required to create Sessions in this SessionGroup'
    )

    max_sessions = IntegerField(
        null=True,
        help_text='Maximum total number of sessions that can be created in this SessionGroup (null = unlimited)'
    )

    max_concurrent = IntegerField(
        null=True,
        help_text='Maximum number of sessions allowed to run at one time for this SessionGroup (null = unlimited)',
    )

    max_queue = IntegerField(
        null=True,
        help_text='Maximum number of users waiting for a new Session to be created in this Session Group '
                  '(null = unlimited)'
    )

    template = ForeignKey(
        'publisher.SessionTemplate',
        related_name='session_groups',
        null=True, on_delete=SET_NULL,
        help_text='The SessionTemplate that defines resources for new sessions in this group.'
    )

    def save(self, *args, **kwargs) -> None:
        if not self.token:
            self.token = generate_session_group_token(self)

        super(SessionGroup, self).save(*args, **kwargs)

    @property
    def truncated_token(self) -> str:
        """Chop out the middle of the token for short display."""
        return "{}...{}".format(self.token[:TRUNCATED_TOKEN_SHOW_CHARACTERS],
                                self.token[-TRUNCATED_TOKEN_SHOW_CHARACTERS:])

    def __str__(self) -> str:
        return "SessionGroup {} [{}]".format(self.truncated_token, self.created.strftime("%Y-%m-%d"))


class SessionStatus(enum.Enum):
    UNKNOWN = 'Unknown'
    NOT_STARTED = 'Not Started'
    RUNNING = 'Running'
    STOPPED = 'Stopped'


class Session(Model):
    """
    An execution Session
    """
    group = ForeignKey(
        SessionGroup,
        null=False,
        on_delete=PROTECT,  # Don't want to delete references if the container is running and we need control still
        related_name='sessions',
        help_text='The SessionGroup that this Session belongs to.'
    )

    url = URLField(
        help_text='URL for API access to administrate this Session'
    )

    started = DateTimeField(
        null=True,
        help_text='DateTime this Session was started'
    )

    stopped = DateTimeField(
        null=True,
        help_text='DateTime this Session was stopped (or that we detected it had stopped)'
    )

    last_check = DateTimeField(
        null=True,
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


class SessionTemplate(Model):
    """
    A template for new Sessions in a SessionGroup, defines what resources it is allocated.
    """
    owner = ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=SET_NULL,
        related_name='session_templates',
        help_text='User who owns the SessionTemplate'
    )

    name = TextField(
        null=False,
        blank=False
    )

    description = TextField(
        null=True,
        blank=True,
        help_text='Optional long description about the SessionTemplate'
    )

    memory = FloatField(
        default=1,
        null=False,
        blank=False,
        help_text='Gigabytes (GB) of memory allocated'
    )

    cpu = FloatField(
        default=1,
        null=False,
        blank=False,
        help_text='CPU shares (out of 100 per CPU) allocated'
    )

    network = FloatField(
        null=True,
        blank=True,
        help_text='Gigabytes (GB) of network transfer allocated. null = unlimited'
    )

    lifetime = IntegerField(
        null=True,
        blank=True,
        help_text='Minutes before the session is terminated. null = unlimited'
    )

    timeout = IntegerField(
        default=60,
        null=False,
        blank=False,
        help_text='Minutes of inactivity before the session is terminated'
    )

    def __str__(self) -> str:
        return self.name
