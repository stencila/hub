import base64
import os
import shutil
from io import BytesIO
from typing import List

from github import Github
from github.ContentFile import ContentFile

from util.files import Files, file_info

# Github API credentials
# Used to authenticate with GitHub API as a OAuth App to get higher rate limits
# See https://developer.github.com/v3/#oauth2-keysecret
# Note that using the credentials of a "Github App" may give lower rate limits
# than using a "OAuth App".
GITHUB_API_CREDENTIALS = os.getenv("GITHUB_API_CREDENTIALS")


def pull_github(source: dict, path: str = ".", secrets: dict = {}, **kwargs) -> Files:
    """
    Pull a GitHub repo/subpath.

    If a user token is provided in `secrets` it will be used to authenticate
    as that user.

    This function uses the GitHub API and so has to make one request
    per file. This means it is (a) slow and (b) uses up a lot of API
    request quota. Creating a `pull_git` would solve these issues and
    could be used for other Git hosting services.
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

    repo_resource = client.get_repo(source["repo"])
    contents = repo_resource.get_contents(subpath)
    if type(contents) is list:
        return pull_directory(repo_resource, contents, path)
    else:
        return pull_file(repo_resource, contents, path)


def pull_file(repo_resource, contents, path: str) -> Files:
    """
    Pull a file from GitHub.

    For files over 1MB it is necessary to use a different API.
    See https://docs.github.com/rest/reference/repos#get-repository-content.
    """
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)

    if contents.size <= 1e6:
        content = contents.content
    else:
        content = repo_resource.get_git_blob(contents.sha).content

    with open(path, "wb") as file:
        shutil.copyfileobj(BytesIO(base64.b64decode(content)), file)  # type: ignore

    return {path: file_info(path)}


def pull_directory(repo_resource, contents_or_subpath, path: str) -> Files:
    """
    Pull a directory from GitHub.
    """
    if os.path.exists(path):
        if not os.path.isdir(path):
            os.unlink(path)
    else:
        os.makedirs(path, exist_ok=True)

    files = {}
    for child in (
        repo_resource.get_contents(contents_or_subpath)
        if type(contents_or_subpath) is str
        else contents_or_subpath
    ):
        child_path = os.path.join(path, child.name)
        if child.type == "dir":
            files.update(pull_directory(repo_resource, child.path, child_path))
        else:
            files.update(pull_file(repo_resource, child, child_path))
    return files
