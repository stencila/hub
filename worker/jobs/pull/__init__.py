from typing import Callable, Dict, List

import config
from jobs.base.job import Job

from .elife import pull_elife
from .gdoc import pull_gdoc
from .github import pull_github
from .http import pull_http
from .plos import pull_plos

# Functions for pulling individual source types
PULL_FUNCS: Dict[str, Callable[[dict, str, str], List[str]]] = {
    "elife": pull_elife,
    "github": pull_github,
    "googledocs": pull_gdoc,
    "http": pull_http,
    "plos": pull_plos,
}


class Pull(Job):
    """
    A job that pulls a source to disk.

    This class delegates to the functions for each type of
    source defined in `PULL_FUNCS`. Each of those functions
    should have the same call signature as this class's `do`
    method (except that project is a path string, rather than an int).
    """

    name = "pull"

    def do(self, source: dict, project: int, path: str):  # type: ignore
        """
        Pull `source` to `path` within `project`.

        :param source:  A dictionary with `type` and any other keys required to
                        pull the source (e.g. urls, authentication tokens).
        :param project: The id of the project to pull the source to
        :param path:    The path, within the project, to pull the source to;
                        could be the path of a directory or file; may not yet exist.
        :returns:       A list of paths, with the project, created by the pull.
        """
        assert isinstance(source, dict), "source must be a dictionary"
        assert "type" in source, "source must have a type"
        assert (
            isinstance(project, int) and project > 0
        ), "project must be a positive integer"
        assert (
            isinstance(path, str) and len(path) > 0
        ), "path must be a non-empty string"

        # Resolve the pull function based on the source type
        typ = source["type"].lower()
        if typ not in PULL_FUNCS:
            raise ValueError("Unknown source type: {}".format(typ))
        pull_func = PULL_FUNCS[typ]

        # Resolve the project directory based on the project id
        project_dir = config.get_project_dir(project)

        return pull_func(source, project_dir, path)
