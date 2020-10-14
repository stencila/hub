import os
from pathlib import Path
from typing import List

from .helpers import HttpSession, begin_pull, end_pull, Files


def pull_http(source: dict, working_dir: str, path: str, **kwargs) -> Files:
    """
    Pull a file from an HTTP source.
    """
    assert "url" in source, "HTTP source must have a URL"

    session = HttpSession()

    temporary_dir = begin_pull(working_dir)
    dest_path = os.path.join(temporary_dir, path)
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    session.pull(source["url"], dest_path)
    return end_pull(working_dir, path, temporary_dir)
