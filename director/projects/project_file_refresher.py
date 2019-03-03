import os

from django.core.files import File

from projects.project_models import Project
from projects.source_item_models import DirectoryEntryType
from projects.source_models import LinkedSourceAuthentication, FileSource
from projects.source_operations import recursive_directory_list, to_utf8, generate_project_storage_directory, \
    utf8_path_join, strip_directory


class ProjectFileRefresher(object):
    """Read files from disk and create/update FileSource in cloud storage with contents."""

    project: Project
    target_directory: str
    authentication: LinkedSourceAuthentication

    def __init__(self, project: Project, target_directory: str, authentication: LinkedSourceAuthentication) -> None:
        self.project = project
        self.target_directory = target_directory
        self.authentication = authentication

    def refresh(self) -> None:
        # build a list of all the files we know about (dict map file name to DirectoryListEntry)
        source_files = {entry.path: entry for entry in
                        recursive_directory_list(self.project, None, self.authentication)}

        # generate the storage directory on disk for files in this project
        project_dir = generate_project_storage_directory(self.target_directory, self.project)

        for root, dirs, files in os.walk(to_utf8(project_dir)):
            for f in files:
                # iterate every file in the project storage directory
                full_disk_file_path = utf8_path_join(root, f)
                relative_disk_file_path = strip_directory(full_disk_file_path, project_dir)

                if relative_disk_file_path in source_files:
                    # if we already have a reference to this file somehow in DB (either FileSource or linked)
                    if source_files[relative_disk_file_path].type == DirectoryEntryType.FILE:
                        # if it is a file

                        if isinstance(source_files[relative_disk_file_path].source, FileSource):
                            # only update contents if it is a FileSource, not if it came from GitHub etc
                            s = FileSource.objects.get(project=self.project, path=relative_disk_file_path)
                            with open(full_disk_file_path, 'rb') as disk_file:
                                s.push(disk_file)
                                s.save()
                        # else: file came from linked source
                else:
                    # Create a new FileSource as reference to this disk file and pull in the contents
                    with open(full_disk_file_path, 'rb') as disk_file:
                        FileSource.objects.create(project=self.project, path=relative_disk_file_path,
                                                  file=File(disk_file))
