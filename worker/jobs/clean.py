import os
import shutil

from jobs.base.job import Job
from util.files import Files, list_files


class Clean(Job):
    """
    A job that cleans a project's working directory.

    Recursively removes all files in the current directory (assumes that
    have already changed into project's working directory) and
    returns a list of files (which should be empty).

    This is equivalent to `rm -rf .` so be very careful where you run
    this job.
    """

    name = "clean"

    def do(  # type: ignore
        self, **kwargs
    ) -> Files:
        for root, dirs, files in os.walk("."):
            for file in files:
                try:
                    os.unlink(os.path.join(root, file))
                except Exception as exc:
                    self.warn(str(exc))
            for dir in dirs:
                try:
                    shutil.rmtree(os.path.join(root, dir))
                except Exception as exc:
                    self.warn(str(exc))
        return list_files()
