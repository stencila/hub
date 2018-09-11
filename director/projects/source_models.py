import enum
from io import BytesIO
import typing

from django.contrib.contenttypes.models import ContentType
from django.db import models
from polymorphic.models import PolymorphicModel


class Source(PolymorphicModel):
    project = models.ForeignKey(
        'projects.Project',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sources'
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

    def pull(self) -> BytesIO:
        raise NotImplementedError('Pull is not implemented for class {}'.format(self.__class__.__name__))

    def push(self, archive: typing.Union[str, typing.IO]) -> None:
        raise NotImplementedError('Push is not implemented for class {}'.format(self.__class__.__name__))


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

    def pull(self) -> BytesIO:
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

    def push(self, archive: typing.Union[str, typing.IO]) -> None:
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


class FilesSourceFile(models.Model):
    """
    A file residing in a `FilesProject`
    """

    source = models.ForeignKey(
        FilesSource,
        related_name='files',
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=1024,
        default='unnamed',
        help_text='Name of the file (a path relative to the project root)'
    )

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

    updated = models.DateTimeField(
        auto_now=True,
        help_text='Time this model instance was last updated'
    )

    modified = models.DateTimeField(
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
