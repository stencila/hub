import os
from typing import Callable, Dict, List

import config
from jobs.base.job import Job

from .elife import pull_elife
from .gdoc import pull_gdoc
from .gdrive import pull_gdrive
from .github import pull_github
from .helpers import Files
from .http import pull_http
from .plos import pull_plos
from .upload import pull_upload

# Functions for pulling individual source types
PULL_FUNCS: Dict[str, Callable[..., Files]] = {
    "elife": pull_elife,
    "github": pull_github,
    "googledocs": pull_gdoc,
    "googledrive": pull_gdrive,
    "http": pull_http,
    "plos": pull_plos,
    "upload": pull_upload,
    "url": pull_http,  # URL is used as an alias for HTTP e.g `UrlSource`
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

    def do(self, source: dict, path: str, secrets: Dict = {}, **kwargs):  # type: ignore
        """
        Pull `source` to `path` within `project`.

        :param source:  A dictionary with `type` and any other keys required to
                        pull the source (e.g. urls, authentication tokens).
        :param path:    The path, within the project, to pull the source to;
                        could be the path of a directory or file; may not yet exist.
        :param secrets: Authentication credentials, API keys and other secrets needed
                        to pull the source. Secrets are not displayed in job listings.
        :returns:       A list of paths, with the project, created by the pull.
        """
        assert isinstance(source, dict), "source must be a dictionary"
        assert "type" in source, "source must have a type"
        assert isinstance(secrets, dict), "secrets must be a dictionary"

        # Resolve the pull function based on the source type
        typ = source["type"].lower()
        if typ not in PULL_FUNCS:
            raise ValueError("Unknown source type: {}".format(typ))
        pull_func = PULL_FUNCS[typ]

        return pull_func(
            source=source, working_dir=os.getcwd(), path=path, secrets=secrets
        )
