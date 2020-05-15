from .base import PullSession


def pull_http(source: dict, sink: str) -> str:
    """
    Pull a file from an HTTP source.
    """
    assert "url" in source, "HTTP source must have a URL"

    session = PullSession()
    session.pull(source["url"], sink)
    return sink
