from typing import List, Union, Dict
import shutil

import config
from jobs.base.job import Job
from util.files import Files, list_files


class Archive(Job):
    """
    A job that archive files from a project's working directory to a snapshots directory.
    """

    name = "archive"

    def do(  # type: ignore
        self, project: int, snapshot: str, **kwargs
    ) -> Files:
        dest = config.get_project_snapshot_dir(project, snapshot)
        shutil.copytree(".", dest)
        shutil.make_archive(dest, "zip", ".")
        return list_files(dest)
