import os
import shutil
from pathlib import Path
from typing import Optional

from util.files import Files, file_info
from util.http import HttpSession


def pull_http(
    source: dict, path: Optional[str] = None, secrets: dict = {}, **kwargs
) -> Files:
    """
    Pull a file from a HTTP source.
    """
    url = source.get("url")
    assert url, "HTTP source must have a URL"

    if not path:
        path = str(os.path.basename(url))

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)

    session = HttpSession()
    session.pull(url, path)

    return {path: file_info(path)}
