import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from zipfile import ZipFile, ZipInfo

import httpx

from util.files import (
    Files,
    bytes_fingerprint,
    ensure_parent,
    file_fingerprint,
    file_info,
    file_mimetype,
)
from util.github_api import github_client


def pull_github(
    source: dict, path: Optional[str] = None, secrets: dict = {}, **kwargs
) -> Files:
    """
    Pull a GitHub repo/subpath.

    If a user token is provided in `secrets` it will be used to authenticate
    as that user.
    """
    assert source.get("repo"), "GitHub source must have a repo"

    subpath = source.get("subpath") or ""
    if subpath.endswith("/"):
        subpath = subpath[:-1]

    path = path or "."

    # Get the possibly token protected link for the repo archive
    # See https://developer.github.com/v3/repos/contents/#download-a-repository-archive
    client = github_client(secrets.get("token"))
    repo_resource = client.get_repo(source["repo"])
    archive_link = repo_resource.get_archive_link("zipball")

    # Get the archive. To avoid it filling up memory, stream directly to file,
    # Increase timeout over the default of 5s.
    zip_file = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    with httpx.stream("GET", archive_link, timeout=60) as response:
        for data in response.iter_bytes():
            zip_file.write(data)
    zip_file.close()

    return pull_zip(zip_file.name, subpath=subpath, path=path)


def pull_zip(
    zip_file: str, subpath: str = "", path: str = ".", strip: int = 1
) -> Files:
    """
    Pull files from a Zip file.

    :param zip_file: The path to the zip file.
    :param subpath: The file or directory in the zip file to extract.
    :param path: The destination path
    :param strip: Number of leading components from filenames to ignore.
                  Similar to `tar`'s `--strip-components` option.
    """
    files = {}

    with ZipFile(zip_file, "r") as zip_archive:
        for zip_info in zip_archive.infolist():
            zip_path = zip_info.filename

            # Skip directories
            if zip_path[-1] == "/":
                continue

            # Remove the first element of the path (the repo name + hash)
            inner_path = os.path.join(*(zip_path.split("/")[strip:]))

            # Save if in the subpath
            remainder_path = None
            if subpath == "":
                remainder_path = inner_path
            elif inner_path.startswith(subpath + "/"):
                chars = len(subpath) + 1
                remainder_path = inner_path[chars:]
            elif inner_path == subpath:
                remainder_path = inner_path

            if remainder_path:
                dest_path = os.path.join(path, remainder_path)

                # Using `extract` is much much faster than reading bytes
                # and then writing them to file. Also it maintains other file info
                # such as modified time in the file written to disk. This speed up
                # is much more important for real world zips than any speed advantage
                # due to not reading bytes twice for fingerprint generation.
                zip_info.filename = dest_path
                zip_archive.extract(zip_info)

                files[remainder_path] = file_info(dest_path)

    return files
