import os
import shutil
from io import BytesIO
from typing import List

from github import Github
from github.ContentFile import ContentFile

from util.files import Files, file_info


def pull_github(source: dict, path: str = ".", secrets: dict = {}, **kwargs) -> Files:
    """
    Pull a GitHub repo/subpath.

    If a token is provided in `secrets` it will be used to authenticate.
    The token could either be an OAuth2 token for a user, or if that
    is not available a OAuth2 key/secret for a client application
    (see https://developer.github.com/v3/#authentication).
    """
    assert source.get("repo"), "GitHub source must have a repo"

    subpath = source.get("subpath") or ""
    if subpath.endswith("/"):
        subpath = subpath[:-1]

    token = secrets.get("token")
    if token is None:
        # Unauthenticated access
        client = Github()
    elif ":" in token:
        # Authenticate as a client application
        # No extra permissions, just higher rate limits
        key, secret = token.split(":")
        client = Github(key, secret)
    else:
        # Authenticate as a user
        client = Github(token)

    repo_resource = client.get_repo(source["repo"])
    contents = repo_resource.get_contents(subpath)
    if type(contents) is list:
        return pull_directory(repo_resource, subpath, path)
    else:
        return pull_file(contents, path)


def pull_file(contents, path: str) -> Files:
    """
    Pull a file from GitHub.
    """
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)

    with open(path, "wb") as file:
        shutil.copyfileobj(BytesIO(contents.decoded_content), file)  # type: ignore

    return {path: file_info(path)}


def pull_directory(repo_resource, repo_subpath: str, path: str) -> Files:
    """
    Pull a directory from GitHub.
    """
    if os.path.exists(path):
        if not os.path.isdir(path):
            os.unlink(path)
    else:
        os.makedirs(path, exist_ok=True)

    files = {}
    for child in repo_resource.get_contents(repo_subpath):
        child_path = os.path.join(path, child.name)
        if child.type == "dir":
            files.update(pull_directory(repo_resource, child.path, child_path))
        else:
            files.update(pull_file(child, child_path))
    return files
