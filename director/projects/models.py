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

    def pull(self):
        """
        Pull files from the project source
        """
        pass

    def push(self, archive):
        """
        Push files to the project source
        """
        pass


class FileProject(Project):
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


def file_project_file_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/file_projects/<id>/<filename>
    return 'file_projects/{0}/{1}'.format(instance.project.id, filename)


class FileProjectFile(Model):
    """
    A file residing in a `FileProject`
    """

    project = ForeignKey(
        FileProject,
        related_name='files',
        on_delete=CASCADE
    )

    file = FileField(
        null=False,
        blank=True,
        upload_to=file_project_file_path
    )


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
