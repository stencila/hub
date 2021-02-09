import os
import shutil

from config import get_snapshot_dir
from jobs.base.job import Job


class Zip(Job):
    """
    A job that creates a Zip file of a project's working directory.

    Currently saves to a path within a snapshot but will be made
    more general in the future so that it saves to the `content` bucket
    and can be used for creating a zip file of the project for download.
    """

    name = "zip"

    def do(  # type: ignore
        self, project: int, snapshot: str, zip_name: str, **kwargs
    ) -> None:
        snapshot_dir = get_snapshot_dir(project, snapshot)
        zip_path = os.path.join(snapshot_dir, os.path.splitext(zip_name)[0])
        shutil.make_archive(zip_path, "zip", ".")
