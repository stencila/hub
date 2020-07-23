import os
import shutil

from config import get_working_dir
from jobs.base.job import Job
from util.files import Files, list_files


class Clean(Job):
    """
    A job that cleans a project's working directory.

    Currently, this removes all files. In the future, it may
    only remove files that are not part of the pipeline
    (i.e. artifacts).
    """

    name = "clean"

    def do(  # type: ignore
        self, project: int, **kwargs
    ) -> Files:
        working_dir = get_working_dir(project)
        for root, dirs, files in os.walk(working_dir):
            for file in files:
                os.unlink(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
        return list_files(working_dir)
