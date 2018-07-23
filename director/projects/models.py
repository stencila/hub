import datetime
from io import BytesIO
from zipfile import ZipFile

from django.db.models import (
    Model,

    CharField,
    DateTimeField,
    IntegerField,
    ForeignKey,
    FileField,
    SlugField,
    TextField,

    CASCADE, SET_NULL
)
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from polymorphic.models import PolymorphicModel


class Project(PolymorphicModel):
    """
    A project
    """

    address = CharField(
        max_length=1024,
        blank=True,
        help_text='Address of project e.g. github://org/repo/folder'
    )

    creator = ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=SET_NULL,
        related_name='projects_created',
        help_text='User who created project'
    )

    def __str__(self):
        return self.address if self.address else 'Project #{}'.format(self.id)

    @staticmethod
    def create(type, creator):
        """
        Create a new editor of the given type
        """
        if type == 'files':
            return FilesProject.objects.create(creator=creator)
        else:
            raise RuntimeError('Unhandled type "{}" when attempting to create project'.format(type))

    @staticmethod
    def get_or_create(type, address, creator):
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

    @property
    def type(self):
        return ContentType.objects.get_for_id(self.polymorphic_ctype_id).model

    def get_name(self):
        """
        A temporary implementation of a name property
        which is likely to be replaced by a db field in future
        """
        return self.address if self.address else 'Unnamed'

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


# Project classes in alphabetaical order
#
# Note: many of these are, obviously, not implemented, but have
# been added here as placeholders, to sketch out the different types of
# project sources that might be avilable
#
# Note: where these derived classes do not need any additional
# fields you can use `class Meta: abstract = True`
# so that an additional database table is not created.
# However, that means that they are not available in the admin.


class BitbucketProject(Project):
    """
    A project hosted on Bitbucket
    """

    class Meta:
        abstract = True


class DatProject(Project):
    """
    A project hosted on Dat
    """

    class Meta:
        abstract = True


class DropboxProject(Project):
    """
    A project hosted on Dropbox
    """

    class Meta:
        abstract = True


class FilesProject(Project):
    """
    A project hosted on Stencila Hub consisting of a set of files
    """

    name = SlugField(
        null=True,
        blank=True,
        help_text='Name of the project'
    )

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
            try:
                instance = FilesProjectFile.objects.get(project=self, name=name)
            except FilesProjectFile.DoesNotExist:
                instance = FilesProjectFile(project=self, name=name)
            # Read the file from the zipfile
            content = BytesIO()
            content.write(zipfile.read(name))
            content.seek(0)
            # Create a new file with contents and name
            instance.file.save(name, content, save=False)
            instance.modified = datetime.datetime.utcnow()
            instance.save()


def files_project_file_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/files_projects/<id>/<filename>
    return 'files_projects/{0}/{1}'.format(instance.project.id, filename)


class FilesProjectFile(Model):
    """
    A file residing in a `FilesProject`
    """

    project = ForeignKey(
        FilesProject,
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
        upload_to=files_project_file_path,
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
        unique_together = ['project', 'name']

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


class GithubProject(Project):
    """
    A project hosted on Github
    """

    class Meta:
        abstract = True


class GitlabProject(Project):
    """
    A project hosted on Gitlab
    """

    class Meta:
        abstract = True


class OSFProject(Project):
    """
    A project hosted on the Open Science Framework

    See https://developer.osf.io/ for API documentation
    """

    class Meta:
        abstract = True
