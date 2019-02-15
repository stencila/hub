import os
import shutil
import typing
from datetime import datetime

from django.utils import timezone
from django.utils.text import slugify

from projects.project_models import ProjectEvent, ProjectEventType
from projects.project_puller import ProjectSourcePuller
from projects.source_operations import generate_project_archive_directory, path_is_in_directory
from .models import Project


class ProjectArchiver(object):
    archive_root: str
    project: Project
    puller: ProjectSourcePuller

    def __init__(self, archive_root: str, project: Project, puller: ProjectSourcePuller) -> None:
        self.archive_root = archive_root
        self.project = project
        self.puller = puller

    def generate_archive_name(self) -> str:
        prefix = slugify(self.project.name)[:32] if self.project.name else ''

        if not prefix:
            prefix = '{}'.format(self.project.id)

        return '{}-{}'.format(prefix, datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

    def archive_project(self, archive_name: typing.Optional[str] = None) -> None:
        self.puller.pull()

        project_dir = self.puller.project_directory

        event = ProjectEvent(event_type=ProjectEventType.ARCHIVE.name, project=self.project)
        event.save()

        if not archive_name:
            archive_name = self.generate_archive_name()

        try:
            output_dir, output_path = self.build_archive_paths(archive_name)
            os.makedirs(output_dir, exist_ok=True)
            shutil.make_archive(output_path, 'zip', project_dir)
            event.success = True
        except Exception as e:
            event.success = False
            event.message = str(e)
            raise
        finally:
            event.finished = timezone.now()
            event.save()

    def build_archive_paths(self, archive_name: str) -> typing.Tuple[str, str]:
        output_dir = generate_project_archive_directory(self.archive_root, self.project)
        output_path = os.path.join(output_dir, archive_name)

        if not path_is_in_directory(output_path, output_dir):
            raise OSError("Archive output path is not inside Project's archive directory.")

        return output_dir, output_path
