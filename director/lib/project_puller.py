import os
import shutil
import typing

from django.http import HttpRequest

from projects.project_models import Project
from projects.source_edit import SourceContentFacade
from projects.source_item_models import DirectoryEntryType
from projects.source_models import LinkedSourceAuthentication
from projects.source_operations import list_project_virtual_directory


class ProjectSourcePuller(object):
    """
    Pulls the files of a `Project` onto the local file system.

    This will combine all the virtual and remote sources (Github, etc) into one directory structure.
    """

    project: Project
    target_directory: str
    authentication: LinkedSourceAuthentication
    request: HttpRequest

    def __init__(self, project: Project, target_directory: str, authentication: LinkedSourceAuthentication,
                 request: HttpRequest) -> None:
        self.project = project
        self.target_directory = target_directory
        self.authentication = authentication
        self.request = request

    @property
    def project_directory(self) -> str:
        """Combine the `target_directory` and project ID."""
        return os.path.join(self.target_directory, '{}'.format(self.project.id))

    def clone(self) -> None:
        """Perform the clone of the project files."""
        shutil.rmtree(self.project_directory)
        os.makedirs(self.project_directory, exist_ok=True)
        self.clone_directory()

    def clone_directory(self, sub_directory: typing.Optional[str] = None) -> None:
        """
        Clone one 'virtual' directory.

        Will create directories and files in `sub_directory`, then recurse into directories to repeat the clone.
        """
        dir_list = list_project_virtual_directory(self.project, sub_directory, self.authentication)

        working_directory = sub_directory or ''
        fs_working_directory = os.path.join(self.project_directory, working_directory)

        for entry in dir_list:
            output_path = os.path.join(fs_working_directory, entry.name)

            if entry.type == DirectoryEntryType.DIRECTORY:
                os.makedirs(output_path, exist_ok=True)
            elif entry.type == DirectoryEntryType.FILE:
                scf = SourceContentFacade(entry.source, self.authentication, self.request, entry.path)
                with open(output_path, 'wb') as f:
                    shutil.copyfileobj(scf.get_binary_content(), f)

        directory_entries = filter(lambda e: e.type == DirectoryEntryType.DIRECTORY, dir_list)

        for directory in directory_entries:
            self.clone_directory(os.path.join(working_directory, directory.name))
