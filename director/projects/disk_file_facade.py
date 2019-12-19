import os
import shutil
import typing
from enum import Enum

from lib.resource_allowance import get_directory_size
from projects.project_models import Project
from projects.source_operations import generate_project_storage_directory, relative_path_join, utf8_path_exists, \
    utf8_makedirs, to_utf8, utf8_isdir, utf8_unlink, utf8_path_join, utf8_basename, utf8_rename, utf8_dirname


class ItemType(Enum):
    FILE = 'file'
    FOLDER = 'folder'


class DiskFileFacade(object):
    project: Project
    project_storage_directory: str

    def __init__(self, project_storage_root: str, project: Project) -> None:
        self.project = project
        self.project_storage_directory = generate_project_storage_directory(project_storage_root, project)

    def full_file_path(self, relative_path: str) -> str:
        """
        Combine the relative path with the root for the Project to build an absolute path.

        `relative_path_join` will raise a `ValueError` if the path is not relative (e.g. if `..` has been used in
        `relative_path`).
        """
        return relative_path_join(self.project_storage_directory, relative_path)

    def create_directory(self, relative_path: str) -> None:
        full_path = self.full_file_path(relative_path)
        utf8_makedirs(full_path, exist_ok=True)

    def create_file(self, relative_path: str) -> None:
        full_path = self.full_file_path(relative_path)
        if utf8_path_exists(full_path):
            raise OSError('Can not create project file at {} as it already exists'.format(full_path))

        utf8_makedirs(utf8_dirname(full_path), exist_ok=True)

        with open(full_path, 'a'):
            pass

    def remove_item(self, relative_path: str) -> None:
        full_path = self.full_file_path(relative_path)
        if not utf8_path_exists(full_path):
            raise OSError('Can not remove {} as it does not exist'.format(full_path))

        if utf8_isdir(full_path):
            shutil.rmtree(to_utf8(full_path))
        else:
            utf8_unlink(full_path)

    def write_file_content(self, relative_path: str, content: typing.Union[str, bytes]) -> None:
        if not self.item_exists(relative_path):
            # takes care of creating the directories etc, even though it is an extra open call
            self.create_file(relative_path)

        if isinstance(content, str):
            mode = 'w'
        else:
            mode = 'wb'

        with open(self.full_file_path(relative_path), mode) as f:
            f.write(content)

    def read_file_content(self, relative_path: str) -> bytes:
        with open(self.full_file_path(relative_path), 'rb') as f:
            return f.read()

    def item_exists(self, relative_path: str) -> bool:
        return utf8_path_exists(self.full_file_path(relative_path))

    def move_file(self, current_relative_path: str, new_relative_path: str) -> None:
        current_path = self.full_file_path(current_relative_path)
        new_path = self.full_file_path(new_relative_path)

        if utf8_isdir(new_path):
            # path moving to is a directory so actually move inside the path
            filename = utf8_basename(current_path)
            new_path = utf8_path_join(new_path, filename)

        if utf8_path_exists(new_path):
            raise OSError(
                'Can not move {} to {} as target file exists.'.format(current_relative_path, new_relative_path))

        utf8_makedirs(utf8_dirname(new_path), exist_ok=True)
        utf8_rename(current_path, new_path)

    def item_type(self, relative_path: str) -> ItemType:
        if not self.item_exists(relative_path):
            raise OSError('Can not determine type of {} as it does not exist.'.format(relative_path))

        full_path = self.full_file_path(relative_path)

        return ItemType.FOLDER if utf8_isdir(full_path) else ItemType.FILE

    def get_size(self, relative_path: str) -> int:
        return os.path.getsize(self.full_file_path(relative_path))

    def get_project_directory_size(self) -> bool:
        return get_directory_size(self.project_storage_directory)
