import os
import typing
import zipfile
from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from lib.data_cleaning import logged_in_or_none
from projects.project_models import ProjectEvent, ProjectEventType, ProjectEventLevel, Snapshot
from projects.project_puller import ProjectSourcePuller
from projects.source_operations import generate_project_archive_directory, generate_project_storage_directory
from lib.path_operations import to_utf8, utf8_path_join, utf8_makedirs, path_is_in_directory, utf8_path_exists
from .models import Project


class Archiver(object):
    archive_root: str

    def __init__(self, archive_root: str) -> None:
        self.archive_root = archive_root

    @staticmethod
    def archive_directory(output_path: str, project_dir: str) -> None:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_handle:
            for root, dirs, files in os.walk(to_utf8(project_dir)):
                for file in files:
                    file_path = utf8_path_join(root, file)
                    relative_path = file_path[len(project_dir):]
                    zip_handle.write(to_utf8(file_path).decode('utf8'), relative_path)

    def generate_project_archive_directory(self) -> str:
        raise NotImplementedError('Subclasses must implement generate_project_archive_directory')

    def build_archive_paths(self, archive_name: str) -> typing.Tuple[str, str]:
        output_dir = self.generate_project_archive_directory()
        output_path = utf8_path_join(output_dir, archive_name.encode('utf8'))

        if not path_is_in_directory(output_path, output_dir):
            raise OSError("Archive output path is not inside Project's archive directory.")

        return output_dir, output_path

    def do_archive(self, project_dir: str, archive_name: str, always_create: bool = True) -> str:
        output_dir, output_path = self.build_archive_paths(archive_name)
        utf8_makedirs(output_dir, exist_ok=True)
        if always_create or not utf8_path_exists(output_path):
            self.archive_directory(output_path, project_dir)
        return output_path


class ProjectArchiver(Archiver):
    project: Project
    puller: ProjectSourcePuller
    user: User

    def __init__(self, archive_root: str, project: Project, user: User, puller: ProjectSourcePuller) -> None:
        super(ProjectArchiver, self).__init__(archive_root)
        self.project = project
        self.puller = puller
        self.user = user

    def generate_archive_name(self, prefix: typing.Optional[str]) -> str:
        prefix = '{}-'.format(prefix) if prefix else ''

        formatted_name = self.project.name[:32]

        if not formatted_name:
            formatted_name = '{}'.format(self.project.id)

        return '{}{}-{}'.format(prefix, formatted_name, datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

    def archive_project(self, name_prefix: typing.Optional[str] = None) -> str:
        self.puller.pull()

        project_dir = self.puller.project_directory

        event = ProjectEvent.objects.create(event_type=ProjectEventType.ARCHIVE.name, project=self.project,
                                            user=logged_in_or_none(self.user),
                                            level=ProjectEventLevel.INFORMATIONAL.value)

        archive_name = self.generate_archive_name(name_prefix)

        try:
            output_path = self.do_archive(project_dir, archive_name)
            event.success = True
        except Exception as e:
            event.level = ProjectEventLevel.ERROR.value
            event.success = False
            event.message = str(e)
            raise
        finally:
            event.finished = timezone.now()
            event.save()

        return output_path

    def generate_project_archive_directory(self) -> str:
        return generate_project_archive_directory(self.archive_root, self.project)


class SnapshotArchiver(Archiver):
    snapshot: Snapshot
    user: User

    def __init__(self, archive_root: str, snapshot: Snapshot, user: User) -> None:
        super().__init__(archive_root)
        self.snapshot = snapshot
        self.user = user

    def generate_archive_name(self) -> str:
        tag = '-{}'.format(self.snapshot.tag) if self.snapshot.tag else ''

        return 'snapshot-{}-v{}{}.zip'.format(self.snapshot.project.name, self.snapshot.version_number, tag)

    def archive_snapshot(self) -> str:
        archive_name = self.generate_archive_name()
        project_dir = generate_project_storage_directory(self.archive_root, self.snapshot.project)
        return self.do_archive(project_dir, archive_name)

    def generate_project_archive_directory(self) -> str:
        return generate_project_archive_directory(self.archive_root, self.snapshot.project)
