from io import BytesIO
from zipfile import ZipFile

from django.db.models import (
    Model,

    CharField,
    ForeignKey,
    FileField,
    TextField,

    CASCADE
)
from polymorphic.models import PolymorphicModel


class Project(PolymorphicModel):
    """
    A project
    """

    address = CharField(
        blank=True,
        help_text='Address of project e.g. github://org/repo/folder'
    )

    @staticmethod
    def create_from_address(address):
        """
        Create a project from an address.
        """
        raise NotImplementedError()

    @staticmethod
    def create_from_url(url):
        """
        Create a project from a URL.

        This method enables users to specify a project
        by copying a third party URL from the browser address bar.
        Converts the URL into an address.For example,

        https://github.com/stencila/examples/tree/master/mtcars

        is converted to,

        github://stencila/examples/mtcars
        """
        raise NotImplementedError()

    def pull(self):
        """
        Pull files from the project source
        """
        raise NotImplementedError()

    def push(self, archive):
        """
        Push files to the project source
        """
        raise NotImplementedError()


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

    def pull(self):
        """
        Pull files from the Django storage into an archive
        """
        archive = BytesIO()
        with ZipFile(archive, mode='w') as zipfile:
            for file in self.files.all():
                # TODO set the path, not the full path
                zipfile.write(file.file.path)
        return archive

    def push(self, archive):
        """
        Push files in the archive to the Django storage
        """
        # Clear the files in this project
        with ZipFile(archive, mode='r') as zipfile:
            pass


def files_project_file_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/file_projects/<id>/<filename>
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
