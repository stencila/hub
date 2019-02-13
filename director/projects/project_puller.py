import os
import shutil
import typing

from django.http import HttpRequest
from django.utils import timezone

from projects.project_models import Project, ProjectEvent, ProjectEventType
from projects.source_edit import SourceContentFacade
from projects.source_item_models import DirectoryEntryType
from projects.source_models import LinkedSourceAuthentication
from projects.source_operations import list_project_virtual_directory, generate_project_storage_directory


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
        return generate_project_storage_directory(self.target_directory, self.project)

    def pull(self) -> None:
        """Perform the pull of the project files."""
        event = ProjectEvent(event_type=ProjectEventType.SOURCE_PULL.name, project=self.project)
        event.save()
        os.makedirs(self.project_directory, exist_ok=True)
        try:
            self.pull_directory()
        except Exception as e:
            event.message = str(e)
            event.finished = timezone.now()
            event.success = False
            event.save()
            raise

        event.finished = timezone.now()
        event.success = True
        event.save()

    def pull_directory(self, sub_directory: typing.Optional[str] = None) -> None:
        """
        Pull one 'virtual' directory to disk.

        Will create directories and files in `sub_directory`, then recurse into directories to repeat the pull.
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
            self.pull_directory(os.path.join(working_directory, directory.name))
