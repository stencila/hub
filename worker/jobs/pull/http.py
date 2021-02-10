import mimetypes
import os
import shutil
from typing import Optional

import httpx

from util.files import Files, ensure_parent, file_ext, file_info, remove_if_dir

GIGABYTE = 1073741824.0
MAX_SIZE = 1  # Maximum file size in Gigabytes


def pull_http(
    source: dict, path: Optional[str] = None, secrets: dict = {}, **kwargs
) -> Files:
    """
    Pull a file from a HTTP source.
    """
    url = source.get("url")
    assert url, "Source must have a URL"

    with httpx.stream("GET", url) as response:
        if response.status_code != 200:
            raise RuntimeError(f"Error when fetching {url}: {response.status_code}")

        size = int(response.headers.get("Content-Length", 0)) / GIGABYTE
        if size > MAX_SIZE:
            RuntimeError(f"Size of file is greater than {MAX_SIZE}GB maximum: {size}GB")

        if not path:
            path = str(os.path.basename(url))
        if not file_ext(path):
            content_type = response.headers.get("Content-Type", "text/html").split(";")[
                0
            ]
            ext = mimetypes.guess_extension(content_type, strict=False)
            path += ext or ".txt"
        ensure_parent(path)
        remove_if_dir(path)

        with open(path, "wb") as file:
            for data in response.iter_bytes():
                file.write(data)

        return {path: file_info(path)}

    return {}
