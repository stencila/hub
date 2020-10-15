import json
import os
import shutil
from io import BytesIO
from typing import List

from github import Github
from github.ContentFile import ContentFile

from util.path_operations import (utf8_isdir, utf8_makedirs, utf8_normpath,
                                  utf8_path_exists, utf8_path_join,
                                  utf8_unlink)

from .helpers import Files, begin_pull, end_pull


def pull_github(source: dict, working_dir: str, path: str, **kwargs) -> Files:
    """
    Pull a GitHub repo/subpath.

    If a token is provided in `source` it will be used to authenticate.
    The token could either be an OAuth2 token for a user, or if that
    is not available a OAuth2 key/secret for a client application
    (see https://developer.github.com/v3/#authentication).
    """
    assert "repo" in source, "source must have a repo"
    assert "subpath" in source, "source must have a subpath"

    subpath = "" if source["subpath"] is None else source["subpath"]
    if subpath.endswith("/"):
        subpath = subpath[:-1]

    token = source.get("token")
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

    gh = client.get_repo(source["repo"])
    local_path = utf8_normpath(utf8_path_join(working_dir, path))
    utf8_makedirs(local_path, exist_ok=True)
    pulled = pull_directory(gh, subpath, local_path)
    return pulled


def pull_directory(gh, remote_parent: str, local_parent: str):
    contents = gh.get_contents(remote_parent)

    if isinstance(contents, ContentFile):
        contents = [contents]

    for content in contents:
        local_path = utf8_path_join(local_parent, content.name)
        if content.type == "dir":
            if utf8_path_exists(local_path) and not utf8_isdir(local_path):
                utf8_unlink(local_path)
            utf8_makedirs(local_path, exist_ok=True)
            pull_directory(gh, content.path, local_path)
        else:
            if utf8_path_exists(local_path) and utf8_isdir(local_path):
                shutil.rmtree(local_path)
            with open(local_path, "wb") as fh:
                file_content = gh.get_contents(content.path).decoded_content
                shutil.copyfileobj(BytesIO(file_content), fh)  # type: ignore
