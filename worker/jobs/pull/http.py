import os
from typing import List

from .base import HttpSession


def pull_http(source: dict, project: str, path: str) -> List[str]:
    """
    Pull a file from an HTTP source.
    """
    assert "url" in source, "HTTP source must have a URL"

    session = HttpSession()
    session.pull(source["url"], os.path.join(project, path))
    return [path]
