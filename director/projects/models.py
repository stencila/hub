import datetime
import enum
import hashlib
import secrets
from io import BytesIO
from zipfile import ZipFile

import typing as typing
from django.db.models import (
    Model,

    BooleanField,
    CharField,
    DateTimeField,
    IntegerField,
    ForeignKey,
    FileField,
    TextField,
    CASCADE, SET_NULL,
    FloatField, PROTECT, URLField)
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from polymorphic.models import PolymorphicModel

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


class Project(Model):
    """
    A project
    """
    creator = ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=SET_NULL,
        related_name='projects_created',
        help_text='User who created project'
    )

    created = DateTimeField(
        auto_now_add=True,
        help_text='When this project was created'
    )

    public = BooleanField(
        default=False,
        help_text='Should this project be publically visible?'
    )

    token = TextField(
        null=True,
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

    session_parameters = ForeignKey(
        'SessionParameters',
        related_name='projects',
        null=True,
        on_delete=CASCADE,
        help_text='The SessionParameters that defines resources and other parameters of new sessions for this Project.'
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
        return 'Unnamed'

    def pull(self):
        """
        Pull files from the project source
        """
        raise NotImplementedError('Pull is not implemented for class {}'.format(self.__class__.__name__))

    def push(self, archive):
        """
        Push files to the project source
        """
        raise NotImplementedError('Push is not implemented for class {}'.format(self.__class__.__name__))

    def save(self, *args, **kwargs) -> None:
        if not self.token:
            self.token = generate_project_token(self)

        super(Project, self).save(*args, **kwargs)

    @property
    def truncated_token(self) -> str:
        """Chop out the middle of the token for short display."""
        return "{}...{}".format(self.token[:TRUNCATED_TOKEN_SHOW_CHARACTERS],
                                self.token[-TRUNCATED_TOKEN_SHOW_CHARACTERS:])


# Source classes in alphabetical order
#
# Note: many of these are, obviously, not implemented, but have
# been added here as placeholders, to sketch out the different types of
# project sources that might be avilable
#
# Note: where these derived classes do not need any additional
# fields you can use `class Meta: abstract = True`
# so that an additional database table is not created.
# However, that means that they are not available in the admin.


class Source(PolymorphicModel):
    project = ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='sources'
    )

    creator = ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=SET_NULL,
        related_name='sources',
        help_text='User who created this source'
    )

    address = CharField(
        max_length=1024,
        blank=True,
        help_text='Address of project e.g. github://org/repo/folder'
    )

    @property
    def type(self) -> typing.Type['Source']:
        return ContentType.objects.get_for_id(self.polymorphic_ctype_id).model

    @property
    def type_name(self) -> str:
        return AvailableSourceType.get_project_type_name(type(self))

    @property
    def type_id(self) -> str:
        return AvailableSourceType.get_project_type_id(type(self))

    def get_absolute_url(self):
        return reverse('source_detail', args=[self.type_id, self.pk])


class BitbucketSource(Source):
    """
    A project hosted on Bitbucket
    """

    class Meta:
        abstract = True


class DatSource(Source):
    """
    A project hosted on Dat
    """

    class Meta:
        abstract = True


class DropboxSource(Source):
    """
    A project hosted on Dropbox
    """

    class Meta:
        abstract = True


class FilesSource(Source):
    """
    A project hosted on Stencila Hub consisting of a set of files
    """

    def serialize(self):
        return {
            'id': self.id,
            'files': [file.serialize() for file in self.files.all()],
        }

    def save(self, *args, **kwargs):
        if not self.address:
            self.address = 'files://{}'.format(self.id)
        super().save(*args, **kwargs)

    def get_name(self):
        return self.name if self.name else 'Unnamed'

    def pull(self):
        """
        Pull files from the Django storage into an archive
        """

        # Write all the files into a zip archive
        archive = BytesIO()
        with ZipFile(archive, 'w') as zipfile:
            for file in self.files.all():
                # For remote storages (e.g. Google Cloud Storage buckets)
                # `file.file.path` is not available, so use `file.file.read()`
                zipfile.writestr(file.name, file.file.read())
        return archive

    def push(self, archive):
        """
        Push files in the archive to the Django storage
        """

        # Unzip all the files and add to this project
        zipfile = ZipFile(archive, 'r')
        for name in zipfile.namelist():
            # Replace existing file or create a new one
            instance = FilesSourceFile.objects.get_or_create(project=self, name=name)

            # Read the file from the zipfile
            content = BytesIO()
            content.write(zipfile.read(name))
            content.seek(0)
            # Create a new file with contents and name
            instance.file.save(name, content, save=False)
            instance.modified = datetime.datetime.now(tz=timezone.utc)
            instance.save()


def files_source_file_path(instance: "FilesSourceFile", filename: str):
    # File will be uploaded to MEDIA_ROOT/files_projects/<id>/<filename>
    return 'files_projects/{0}/{1}'.format(instance.source.id, filename)


class FilesSourceFile(Model):
    """
    A file residing in a `FilesProject`
    """

    source = ForeignKey(
        FilesSource,
        related_name='files',
        on_delete=CASCADE
    )

    name = CharField(
        max_length=1024,
        default='unnamed',
        help_text='Name of the file (a path relative to the project root)'
    )

    size = IntegerField(
        null=True,
        blank=True,
        help_text='Size of the file in bytes'
    )

    file = FileField(
        null=False,
        blank=True,
        upload_to=files_source_file_path,
        help_text='The actual file stored'
    )

    updated = DateTimeField(
        auto_now=True,
        help_text='Time this model instance was last updated'
    )

    modified = DateTimeField(
        null=True,
        blank=True,
        help_text='Time the file was last modified'
    )

    class Meta:
        pass
        # unique_together = ['source', 'name']  # this constraint is not necessary

    def serialize(self):
        """
        Serialize to a dict for conversion
        to JSON
        """
        return {
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'modified': self.modified,
            'current': True  # Used to distinguish already uploaded files in UI
        }

    def save(self, *args, **kwargs):
        """
        Override of save() to update the size
        property from the file size
        """
        self.size = self.file.size
        super().save(*args, **kwargs)


class GithubSource(Source):
    """
    A project hosted on Github
    """

    class Meta:
        abstract = True


class GitlabSource(Source):
    """
    A project hosted on Gitlab
    """

    class Meta:
        abstract = True


class OSFSource(Source):
    """
    A project hosted on the Open Science Framework

    See https://developer.osf.io/ for API documentation
    """

    class Meta:
        abstract = True


class SourceType(typing.NamedTuple):
    id: str
    name: str
    model: typing.Type


class AvailableSourceType(enum.Enum):
    FILE = SourceType('files', 'Files', FilesSource)

    @classmethod
    def setup_type_lookup(cls) -> None:
        if not hasattr(cls, "_type_lookup"):
            cls._type_lookup = {
                source_type.value.model: source_type.value for source_type in cls
            }

    @classmethod
    def get_project_type_name(cls, model: typing.Type[Source]) -> str:
        cls.setup_type_lookup()
        return cls._type_lookup[model].name

    @classmethod
    def get_project_type_id(cls, model: typing.Type[Source]) -> str:
        cls.setup_type_lookup()
        return cls._type_lookup[model].id
