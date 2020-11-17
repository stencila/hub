import os
import tempfile
from pathlib import Path
from typing import List, Optional
from zipfile import ZipFile

import httpx
from github import Github

from util.files import Files, file_info

# Github API credentials
# Used to authenticate with GitHub API as a OAuth App to get higher rate limits
# See https://developer.github.com/v3/#oauth2-keysecret
# Note that using the credentials of a "Github App" may give lower rate limits
# than using a "OAuth App".
GITHUB_API_CREDENTIALS = os.getenv("GITHUB_API_CREDENTIALS")


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

    token = secrets.get("token")
    if token:
        # Authenticate as a user
        client = Github(token)
    elif GITHUB_API_CREDENTIALS:
        # Authenticate as a OAuth client application
        # No extra permissions, just higher rate limits
        client_id, client_secret = GITHUB_API_CREDENTIALS.split(":")
        client = Github(client_id, client_secret)
    else:
        # Unauthenticated access
        client = Github()

    path = path or "."

    # Get the possibly token protected link for the repo archive
    # See https://developer.github.com/v3/repos/contents/#download-a-repository-archive
    repo_resource = client.get_repo(source["repo"])
    archive_link = repo_resource.get_archive_link("zipball")

    # Get the archive. To avoid it filling up memory, stream directly to file
    zip_file = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    with httpx.stream("GET", archive_link) as response:
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
    with ZipFile(zip_file, "r") as zip_archive:
        files = {}
        for zip_path in zip_archive.namelist():
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
                data = zip_archive.read(zip_path)

                dest_path = (
                    os.path.join(path, remainder_path) if remainder_path else path
                )
                Path(dest_path).parent.mkdir(parents=True, exist_ok=True)

                dest_file = open(dest_path, "wb")
                dest_file.write(data)
                dest_file.close()

                files[remainder_path] = file_info(dest_path)

    return files
