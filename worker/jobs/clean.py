import os
import shutil

from config import get_working_dir
from jobs.base.job import Job
from util.files import Files, list_files


class Clean(Job):
    """
    A job that cleans a project's working directory.

    Removes all files in the current directory (assumes that
    have already changed into project's working directory) and
    returns a list of files (which should be empty).
    """

    name = "clean"

    def do(  # type: ignore
        self, **kwargs
    ) -> Files:
        for root, dirs, files in os.walk("."):
            for file in files:
                os.unlink(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
        return list_files()
