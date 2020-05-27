from typing import Callable, Dict, List

import config
from jobs.base.job import Job

from .gdoc import push_gdoc

# Functions for pushing individual source types
PUSH_FUNCS: Dict[str, Callable[[List[str], str, dict], None]] = {
    "googledocs": push_gdoc,
}


class Push(Job):
    """
    A job that pushes files from a project back to their source.
    """

    name = "push"

    def do(self, paths: List[str], project: int, source: dict):  # type: ignore
        """
        Push `paths` within `project` to `source`.

        :param paths:   A list of paths, within the project, to be pushed.
        :param project: The id of the project to push the paths from
        :param source:  A dictionary with `type` and any other keys required to
                        push the source (e.g. urls, authentication tokens).
        """
        assert isinstance(source, dict), "source must be a dictionary"
        assert "type" in source, "source must have a type"
        assert (
            isinstance(project, int) and project > 0
        ), "project must be a positive integer"
        assert isinstance(paths, list) and len(paths) > 0, "paths must be non-empty"

        # Resolve the push function based on the source type
        typ = source["type"].lower()
        if typ not in PUSH_FUNCS:
            raise ValueError("Unknown source type: {}".format(typ))
        push_func = PUSH_FUNCS[typ]

        # Resolve the project directory based on the project id
        project_dir = config.get_project_dir(project)

        return push_func(paths, project_dir, source)
