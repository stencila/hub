import datetime
import hashlib
import secrets
from io import BytesIO
import typing
from zipfile import ZipFile

from django.db import models
from django.contrib.contenttypes.models import ContentType
from polymorphic.models import PolymorphicModel

from accounts.models import Account
from .permission_models import ProjectPermission, ProjectRole, UserProjectRole
from .session_models import *

TOKEN_HASH_FUNCTION = hashlib.sha256
PROJECT_KEY_LENGTH = 32
TRUNCATED_TOKEN_SHOW_CHARACTERS = 8


def generate_project_key() -> str:
    """Generate a random key for a SessionGroup."""
    return secrets.token_hex(PROJECT_KEY_LENGTH)


def generate_project_token(project: 'Project') -> str:
    """Generate a unique token for a Project based on its creator, creation date and a random string."""
    user_id = project.creator.id if project.creator else None
    created = project.created or datetime.datetime.now()
    return TOKEN_HASH_FUNCTION("{}{}{}".format(user_id, created, secrets.token_hex()).encode("utf8")).hexdigest()


class Project(models.Model):
    """
    A project
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='projects',
        null=False
    )

    name = models.TextField(
        null=True,
        blank=True,
        help_text="The name of the project"
    )

    creator = models.ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=models.SET_NULL,
        related_name='projects_created',
        help_text='User who created project'
    )

    created = models.DateTimeField(
        auto_now_add=True,
        help_text='When this project was created'
    )

    public = models.BooleanField(
        default=False,
        help_text='Should this project be publicly visible?'
    )

    token = models.TextField(
        null=True,
        blank=True,
        unique=True,
        help_text='A token to identify this project (in URLs etc)'
    )

    key = models.TextField(
        null=True,
        blank=True,
        help_text='Key required to create sessions for this project'
    )

    sessions_max = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum total number of sessions that can be created for this project (null = unlimited)'
    )

    sessions_concurrent = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum number of sessions allowed to run at one time for this project (null = unlimited)',
    )

    sessions_queued = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum number of queued requests for a session for this project (null = unlimited)'
    )

    session_parameters = models.ForeignKey(
        'SessionParameters',
        related_name='projects',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='The parameters that defines sessions created for this project'
    )

    def __str__(self):
        return 'Project #{}'.format(self.id)

    @staticmethod
    def create(project_type, creator):
        """
        Create a new editor of the given project_type
        """
        if project_type == 'files':
            return FilesSource.objects.create(creator=creator)
        else:
            raise RuntimeError('Unhandled project type "{}" when attempting to create project'.format(project_type))

    @staticmethod
    def get_or_create(project_type, address, creator):
        """
        Get, or create, a project
        """
        return Project.objects.get_or_create(
            address=address,
            creator=creator
        )

    @staticmethod
    def get_or_create_from_address(address, creator):
        """
        Get, or create, a project from an address.
        """
        # TODO Transform the address into type etc
        return Project.get_or_create(
            type=None,
            address=address,
            creator=creator
        )

    @staticmethod
    def get_or_create_from_url(url, creator):
        """
        Get, or create, a project from a URL.

        This method enables users to specify a project
        by copying a third party URL from the browser address bar.
        Converts the URL into an address.For example,

        https://github.com/stencila/examples/tree/master/mtcars

        is converted to,

        github://stencila/examples/mtcars
        """
        # TODO Transform the URL into an address
        address = url
        return Project.get_or_create_from_address(address, creator)

    def get_name(self):
        """
        A temporary implementation of a name property
        which is likely to be replaced by a db field in future
        """
        return self.name or 'Unnamed'

    def get_first_source(self) -> "Source":
        source = self.sources.first()  # TODO: Update this when UI supports multiple sources
        if not source:
            raise ValueError("This project has no sources")

        return source

    def pull(self) -> BytesIO:
        """
        Pull files from the project source
        """
        return self.get_first_source().pull()

    def push(self, archive: typing.IO) -> None:
        """
        Push files to the project source
        """
        self.get_first_source().push(archive)

    def save(self, *args, **kwargs) -> None:
        if not self.token:
            self.token = generate_project_token(self)

        super(Project, self).save(*args, **kwargs)

    @property
    def truncated_token(self) -> str:
        """Chop out the middle of the token for short display."""
        return "{}...{}".format(self.token[:TRUNCATED_TOKEN_SHOW_CHARACTERS],
                                self.token[-TRUNCATED_TOKEN_SHOW_CHARACTERS:])
