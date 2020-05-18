"""Module for worker and job configuration."""

import os


def get_project_dir(project_id: int):
    """
    Get the path to a project's directory from its id.

    Most jobs are done within the context of a project's
    directory. This method translates a project integer id
    into a local filesystem path on the worker. This allows
    for workers to customize where the projects are stored.
    """
    projects_dir = os.environ.get("PROJECTS_DIR", "projects")
    return os.path.join(projects_dir, str(project_id))
