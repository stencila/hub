import enum
import mimetypes
from io import BytesIO
import typing

from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from polymorphic.models import PolymorphicModel


class MimeTypeFromPathMixin(object):
    path: str

    @property
    def mimetype(self) -> str:
        mimetype, encoding = mimetypes.guess_type(self.path, False)
        return mimetype or 'Unknown'


class Source(PolymorphicModel, MimeTypeFromPathMixin):
    provider_name = ''

    project = models.ForeignKey(
        'Project',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sources'
    )

    path = models.TextField(
        null=False,
        default='.',
        help_text='The path that the file or directory from the source is mapped to in the project'
    )

    updated = models.DateTimeField(
        auto_now=True,
        help_text='Time this model instance was last updated'
    )

    def __str__(self):
        return "Source {}".format(self.path)

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

    def pull(self) -> BytesIO:
        raise NotImplementedError('Pull is not implemented for class {}'.format(self.__class__.__name__))

    def push(self, archive: typing.Union[str, typing.IO]) -> None:
        raise NotImplementedError('Push is not implemented for class {}'.format(self.__class__.__name__))


# Source classes in alphabetical order
#
# Note: many of these are, obviously, not implemented, but have
# been added here as placeholders, to sketch out the different types of
# project sources that might be available
#
# Note: where these derived classes do not need any additional
# fields you can use `class Meta: abstract = True`
# so that an additional database table is not created.
# However, that means that they are not available in the admin.


class BitbucketSource(Source):
    """A project hosted on Bitbucket."""

    provider_name = 'BitBucket'

    class Meta:
        abstract = True


class DatSource(Source):
    """A project hosted on Dat."""

    provider_name = 'Dat'

    class Meta:
        abstract = True


class DropboxSource(Source):
    """A project hosted on Dropbox."""

    provider_name = 'Drop Box'

    class Meta:
        abstract = True


def files_source_file_path(instance: "FileSource", filename: str):
    # File will be uploaded to MEDIA_ROOT/files_projects/<id>/<filename>
    return 'projects/{0}/{1}'.format(instance.id, filename)


class FileSource(Source):
    """A file uploaded to the Hub."""

    provider_name = 'File'

    size = models.IntegerField(
        null=True,
        blank=True,
        help_text='Size of the file in bytes'
    )

    file = models.FileField(
        null=False,
        blank=True,
        upload_to=files_source_file_path,
        help_text='The actual file stored'
    )

    def save(self, *args, **kwargs):
        """Override of base superclass `save` method to update the size property from the file size."""
        if self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)

    def pull(self):
        """Pull the file content."""
        if self.file:
            with self.file.open() as file:
                return file.read().decode()
        else:
            return ''

    def pull_binary(self) -> typing.Optional[bytearray]:
        if self.file:
            return self.file.open('rb').read()
        return None

    def push(self, archive: typing.Union[str, typing.IO]):
        if isinstance(archive, str):
            f = ContentFile(archive)
        else:
            f = File(archive)
        self.file.save(self.path, f)
        self.size = self.file.size


class GithubSource(Source):
    """A project hosted on Github."""

    provider_name = 'GitHub'

    repo = models.TextField(
        null=False,
        blank=False,
        help_text='The Github repository identifier i.e. org/repo'
    )

    subpath = models.TextField(
        null=True,
        blank=True,
        help_text='Path to file or folder withing the repository'
    )

    def __str__(self) -> str:
        return '{}/{}'.format(self.repo, self.subpath or '')


class GitlabSource(Source):
    """A project hosted on Gitlab."""

    provider_name = 'GitLab'

    class Meta:
        abstract = True


class OSFSource(Source):
    """
    A project hosted on the Open Science Framework.

    See https://developer.osf.io/ for API documentation.
    """

    provider_name = 'OSF'

    class Meta:
        abstract = True


class SourceType(typing.NamedTuple):
    """
    Identifying information for a Source Type.

    id: short unique identifier
    name: display name
    model: the Source subclass
    """

    id: str
    name: str
    model: typing.Type


class AvailableSourceType(enum.Enum):
    """Enum for each available SourceType. For two-way lookup name to values etc."""

    FILE = SourceType('file', 'File', FileSource)
    GITHUB = SourceType('github', 'Github', GithubSource)

    # _type_lookup type checking is ignored throughout because it must be added at runtime to the class but then mypy
    # doesn't understand this

    @classmethod
    def setup_type_lookup(cls) -> None:
        if not hasattr(cls, "_type_lookup"):
            cls._type_lookup = {  # type: ignore
                source_type.value.model: source_type.value for source_type in cls
            }

    @classmethod
    def get_project_type_name(cls, model: typing.Type[Source]) -> str:
        cls.setup_type_lookup()
        return cls._type_lookup[model].name  # type: ignore

    @classmethod
    def get_project_type_id(cls, model: typing.Type[Source]) -> str:
        cls.setup_type_lookup()
        return cls._type_lookup[model].id  # type: ignore


class LinkedSourceAuthentication(object):
    """Container for token(s) a user has for authenticating to remote sources."""

    github_token: typing.Optional[str]

    def __init__(self, github_token: typing.Optional[str] = None) -> None:
        self.github_token = github_token
