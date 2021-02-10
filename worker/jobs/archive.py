import shutil
from typing import Optional

from config import get_snapshot_dir
from jobs.base.job import Job
from util.files import Files, list_files


class Archive(Job):
    """
    A job that archive files from a project's working directory to a snapshot directory.
    """

    name = "archive"

    def do(  # type: ignore
        self, project: int, snapshot: str, **kwargs
    ) -> Files:
        files = list_files()
        snapshot_dir = get_snapshot_dir(project, snapshot)
        shutil.copytree(".", snapshot_dir)
        return files
