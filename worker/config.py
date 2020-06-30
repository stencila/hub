"""Module for worker and job configuration."""

import os

HERE = os.path.dirname(__file__)


def get_project_working_dir(project_id: int):
    """
    Get the path to a project's working directory.

    Most jobs are done within the context of a project's
    working directory. This method translates a project integer id
    into a local filesystem path on the worker. This allows
    for workers to customize where the projects are stored.
    """
    return os.path.join(
        os.environ.get("WORKING_DIR", os.path.join(HERE, "working")), str(project_id)
    )


def get_project_snapshot_dir(project_id: int, snapshot_id: int):
    """
    Get the path to a project snapshot directory.

    Snapshots may be on a different filesystem from the project
    working directories.
    """
    return os.path.join(
        os.environ.get("SNAPSHOT_DIR", os.path.join(HERE, "snapshots")),
        str(project_id),
        str(snapshot_id),
    )
