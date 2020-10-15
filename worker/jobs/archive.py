import os
import shutil
from typing import Dict, List, Optional, Union

from config import get_snapshot_dir
from jobs.base.job import Job
from util.files import Files, list_files


class Archive(Job):
    """
    A job that archive files from a project's working directory to a snapshots directory.
    """

    name = "archive"

    def do(  # type: ignore
        self, project: int, snapshot: str, zip_name: Optional[str], **kwargs
    ) -> Files:
        files = list_files(".")
        dest = get_snapshot_dir(project, snapshot)
        shutil.copytree(".", dest)
        if zip_name:
            shutil.make_archive(
                os.path.join(dest, os.path.splitext(zip_name)[0]), "zip", "."
            )
        return files
