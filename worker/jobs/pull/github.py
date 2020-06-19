import json
import os
import shutil

from github import Github
from github.ContentFile import ContentFile
from io import BytesIO
from typing import List

from util.path_operations import (
    utf8_path_join,
    utf8_normpath,
    utf8_makedirs,
    utf8_path_exists,
    utf8_isdir,
    utf8_unlink,
)


def pull_github(source: dict, project: str, path: str) -> List[str]:
    """
    Pull github repo/subpath using given user token
    """
    assert "repo" in source, "source must have a repo"
    assert "subpath" in source, "source must have a subpath"
    assert "token" in source, "source must include a token"

    subpath = "" if source["subpath"] is None else source["subpath"]
    if subpath.endswith("/"):
        subpath = subpath[:-1]

    gh = Github(source["token"]).get_repo(source["repo"])
    local_path = utf8_normpath(utf8_path_join(project, path))
    utf8_makedirs(local_path, exist_ok=True)
    pulled = pull_directory(gh, subpath, local_path)
    return pulled


def pull_directory(gh, remote_parent: str, local_parent: str) -> List[str]:
    pulled = []
    contents = gh.get_contents(remote_parent)

    if isinstance(contents, ContentFile):
        contents = [contents]

    for content in contents:
        local_path = utf8_path_join(local_parent, content.name)
        if content.type == "dir":
            if utf8_path_exists(local_path) and not utf8_isdir(local_path):
                utf8_unlink(local_path)
            utf8_makedirs(local_path, exist_ok=True)
            pulled += pull_directory(gh, content.path, local_path)
        else:
            if utf8_path_exists(local_path) and utf8_isdir(local_path):
                shutil.rmtree(local_path)
            with open(local_path, "wb") as fh:
                file_content = gh.get_contents(content.path).decoded_content
                shutil.copyfileobj(BytesIO(file_content), fh)  # type: ignore
        pulled.append(local_path)
    return pulled
