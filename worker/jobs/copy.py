from typing import List, Union, Dict
import shutil

import config
from jobs.base.job import Job
from util.files import Files, list_files


class Copy(Job):
    """
    A job that copies files from a project's working directory to its snapshots directory.
    """

    name = "copy"

    def do(  # type: ignore
        self, project: int, snapshot: int, **kwargs
    ) -> Files:
        dest = config.get_project_snapshot_dir(project, snapshot)
        shutil.copytree(".", dest)
        shutil.make_archive(dest, "zip", ".")
        return list_files(dest)
