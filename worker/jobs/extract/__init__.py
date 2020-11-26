from typing import Callable, Dict, Optional

from stencila.schema.types import Review

from jobs.base.job import Job

from .gdrive import extract_gdrive

# Functions for extracting reviews from alternative source types
EXTRACT_FUNCS: Dict[str, Callable[..., Review]] = {
    "googledocs": extract_gdrive,
    "googlesheets": extract_gdrive,
    "googledrive": extract_gdrive,
}


class Extract(Job):
    """
    A job that extracts a review from a source.

    This class delegates to the functions for each type of
    source defined in `EXTRACT_FUNCS`. Each of those functions
    should have the same call signature as this class's `do`
    method.
    """

    name = "extract"

    def do(  # type: ignore
        self,
        source: Dict,
        filters: Optional[Dict] = {},
        secrets: Optional[Dict] = {},
        **kwargs,
    ) -> Optional[Review]:
        """
        Extract a review.

        :param source:  A dictionary with `type` and other keys needed to identify the
                        source e.g. ids.
        :param filters: A dictionary of {field:regex} to use to filter comments.
        :param secrets: Authentication credentials, API keys and other secrets needed
                        to access the source.
        :returns:       A `Review` instance or `None`.
        """
        assert isinstance(source, dict), "source must be a dictionary"
        assert "type" in source, "source must have a type"
        assert isinstance(filters, dict), "filters must be a dictionary"
        assert isinstance(secrets, dict), "secrets must be a dictionary"

        typ = source["type"].lower()
        if typ not in EXTRACT_FUNCS:
            raise ValueError("Unknown source type: {}".format(typ))
        extract_func = EXTRACT_FUNCS[typ]

        return extract_func(source=source, filters=filters, secrets=secrets)
