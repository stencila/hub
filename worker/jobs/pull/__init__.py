from jobs.base.job import Job

from .elife import pull_elife
from .http import pull_http

PROVIDERS = {"elife": pull_elife, "http": pull_http}


class Pull(Job):
    """
    A job that pulls a source to disk.
    """

    name = "pull"

    def do(self, source: dict, sink: str):
        """
        Do the pull of `source` to `sink`.

        source: a dictionary with `provider`, and other data required to
                pull the source e.g. authentication tokens depending
                on the provider.
        sink: the file path to pull the source to; could be the path of
              a directory or file; may not yet exist.
        """
        assert "provider" in source, "Source must have a provider"

        provider = source["provider"]

        if provider not in PROVIDERS:
            raise Exception("Unhandled source provider: {}".format(provider))

        return PROVIDERS[provider](source, sink)
