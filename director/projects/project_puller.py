import shutil
import typing
from io import BytesIO

from django.contrib import messages
from django.http import HttpRequest
from django.utils import timezone

from lib.resource_allowance import get_directory_size, StorageLimitExceededException
from projects.project_models import Project, ProjectEvent, ProjectEventType, ProjectEventLevel
from projects.source_content_facade import make_source_content_facade
from projects.source_item_models import DirectoryEntryType
from projects.source_models import LinkedSourceAuthentication, DiskSource
from projects.source_operations import list_project_virtual_directory, generate_project_storage_directory
from lib.path_operations import to_utf8, utf8_path_join, utf8_isdir, utf8_path_exists, utf8_unlink, utf8_makedirs


class ProjectSourcePuller(object):
    """
    Pulls the files of a `Project` onto the local file system.

    This will combine all the virtual and remote sources (Github, etc) into one directory structure.
    """

    project: Project
    target_directory: str
    authentication: LinkedSourceAuthentication
    request: HttpRequest
    storage_limit: int
    current_storage: typing.Optional[int] = None

    def __init__(self, project: Project, target_directory: str, authentication: LinkedSourceAuthentication,
                 request: HttpRequest, storage_limit: int) -> None:
        self.project = project
        self.target_directory = target_directory
        self.authentication = authentication
        self.request = request
        self.storage_limit = storage_limit

    @property
    def project_directory(self) -> str:
        """Combine the `target_directory` and project ID."""
        return generate_project_storage_directory(self.target_directory, self.project)

    def pull(self, only_file_sources: bool = False) -> None:
        """Perform the pull of the project files."""
        event = ProjectEvent.objects.create(event_type=ProjectEventType.SOURCE_PULL.name, project=self.project,
                                            user=self.request.user, level=ProjectEventLevel.INFORMATIONAL.value)
        utf8_makedirs(self.project_directory, exist_ok=True)
        try:
            self.pull_directory(only_file_sources=only_file_sources)
            event.success = True
        except Exception as e:
            event.message = str(e)
            event.level = ProjectEventLevel.ERROR.value
            event.success = False
            raise
        finally:
            event.finished = timezone.now()
            event.save()

    def pull_directory(self, sub_directory: typing.Optional[str] = None, only_file_sources: bool = True) -> None:
        """
        Pull one 'virtual' directory to disk.

        Will create directories and files in `sub_directory`, then recurse into directories to repeat the pull.
        """
        if self.current_storage is None:
            self.current_storage = self.project_directory_size

        dir_list = list_project_virtual_directory(self.project, sub_directory, self.authentication, only_file_sources)

        working_directory = sub_directory or ''
        fs_working_directory = utf8_path_join(self.project_directory, working_directory)

        for entry in dir_list:
            output_path = utf8_path_join(fs_working_directory, entry.name)

            if entry.type in (DirectoryEntryType.DIRECTORY, DirectoryEntryType.LINKED_SOURCE):
                if utf8_path_exists(output_path) and not utf8_isdir(output_path):
                    utf8_unlink(output_path)  # remove path if is a file

                utf8_makedirs(output_path, exist_ok=True)
            else:
                scf = make_source_content_facade(self.request.user, entry.path, entry.source, self.project)

                if self.storage_limit != -1:
                    if isinstance(entry.source, DiskSource):
                        source_size = 0
                    else:
                        source_size = scf.get_size()

                    if source_size + self.current_storage > self.storage_limit:
                        raise StorageLimitExceededException()

                    self.current_storage += source_size

                if utf8_path_exists(output_path) and utf8_isdir(output_path):
                    shutil.rmtree(to_utf8(output_path))  # remove path if it is a directory

                with open(to_utf8(output_path), 'wb') as f:
                    shutil.copyfileobj(BytesIO(scf.get_binary_content()), f)

                if scf.error_exists:
                    for message in scf.message_iterator():
                        messages.add_message(self.request, message.level, message.message)
                    return

        directory_entries = filter(lambda e: e.type in (DirectoryEntryType.DIRECTORY, DirectoryEntryType.LINKED_SOURCE),
                                   dir_list)

        for directory in directory_entries:
            self.pull_directory(utf8_path_join(working_directory, directory.name))

    @property
    def project_directory_size(self) -> int:
        return get_directory_size(self.project_directory)
