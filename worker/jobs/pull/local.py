import os
import shutil

from .helpers import begin_pull, end_pull, Files


def pull_local(source: dict, working_dir: str, path: str) -> Files:
    """
    Pull a path from the local filesystem into a project's working directory.

    Mostly only used in development to pull an "uploaded" files into
    a project (in production uploaded files are pulled from a bucket).
    """
    assert "path" in source, "Local source must have a path"
    source_path = source["path"]
    assert os.path.exists(source_path), "Path must exist on the worker"

    temporary_dir = begin_pull(working_dir)
    dest_path = os.path.join(temporary_dir, path)
    if os.path.isdir(source_path):
        shutil.copytree(source_path, dest_path)
    else:
        shutil.copyfile(source_path, dest_path)
    return end_pull(working_dir, path, temporary_dir)
