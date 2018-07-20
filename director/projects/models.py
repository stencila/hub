from io import BytesIO
import re
from zipfile import ZipFile

from django.db.models import (
    Model,

    CharField,
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
# fields it is tempting to define them as `class Meta: abstract = True`
# so that an additional database table is not created.
# However, that means that they are not available in the admin
# so we currently avoid that optimisation.


class BitbucketProject(Project):
    """
    A project hosted on Bitbucket
    """

    pass


class DatProject(Project):
    """
    A project hosted on Dat
    """

    pass


class DropboxProject(Project):
    """
    A project hosted on Dropbox
    """

    pass


class FilesProject(Project):
    """
    A project hosted on Stencila Hub consisting of a set of files
    """

    # ROOT = os.path.join(configMEDIA_ROOT, 'files_projects')

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
                zipfile.write(file.file.path, file.name)
        return archive

    def push(self, archive):
        """
        Push files in the archive to the Django storage
        """

        # Clear the files in this project
        self.files.all().delete()

        # Unzip all the files and add to this project
        zipfile = ZipFile(archive, 'r')
        for name in zipfile.namelist():
            FilesProjectFile.objects.create(
                project=self,
                file=File(zipfile.open(name, 'r'))
            )


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

    file = FileField(
        null=False,
        blank=True,
        upload_to=files_project_file_path
    )

    @property
    def name(self):
        return re.match(r'files_projects/\d+/(.*)', self.file.name).group(1)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'size': self.file.size
        }


class GithubProject(Project):
    """
    A project hosted on Github
    """

    pass


class GitlabProject(Project):
    """
    A project hosted on Gitlab
    """

    pass


class OSFProject(Project):
    """
    A project hosted on the Open Science Framework

    See https://developer.osf.io/ for API documentation
    """

    pass
