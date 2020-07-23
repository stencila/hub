"""Module for worker and job configuration."""

import os

STORAGE_ROOT = os.environ.get(
    "STORAGE_ROOT", os.path.join(os.path.dirname(__file__), "..", "storage", "data")
)


def get_working_dir(project_id: int):
    """
    Get the path to a project's working directory.

    Most jobs are done within the context of a project's
    working directory. This method translates a project integer id
    into a local filesystem path on the worker. This allows
    for workers to customize where the projects are stored.
    """
    return os.path.join(
        os.environ.get("WORKING_DIR", os.path.join(STORAGE_ROOT, "working")),
        str(project_id),
    )


def get_snapshot_dir(snapshot_path: str) -> str:
    """
    Get the path to a project snapshot directory.

    Snapshots may be on a different filesystem from the project
    working directories.
    """
    return os.path.join(
        os.environ.get("SNAPSHOT_DIR", os.path.join(STORAGE_ROOT, "snapshots")),
        snapshot_path,
    )
