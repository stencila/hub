import json
import os
import shutil
import typing

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.client import GoogleCredentials
from typing import List

from util.path_operations import (
    utf8_path_join,
    utf8_normpath,
    utf8_makedirs,
    utf8_path_exists,
    utf8_isdir,
    utf8_unlink,
)


def pull_gdrive(source: dict, project: str, path: str) -> List[str]:
    """
    Pull a google drive folder
    """
    assert "folder_id" in source, "source must have a folder_id"
    assert (
        "token" in source and source["token"] is not None
    ), "source must include a token"

    credentials = GoogleCredentials(
        source["token"], None, None, None, None, None, "Stencila Hub Client",
    )
    drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    files_resource = drive_service.files()

    return pull_directory(
        files_resource,
        source["folder_id"],
        utf8_normpath(utf8_path_join(project, path)),
    )


def pull_directory(files_resource, drive_parent: str, local_parent: str) -> List[str]:
    pulled = []

    for f in list_folder(files_resource, drive_parent):
        local_path = utf8_path_join(local_parent, f["name"])
        if f["mimeType"] == "application/vnd.google-apps.folder":
            if utf8_path_exists(local_path) and not utf8_isdir(local_path):
                utf8_unlink(local_path)
            utf8_makedirs(local_path)
            pulled += pull_directory(files_resource, f["id"], local_path)
        else:
            if f["mimeType"].startswith("application/vnd.google-apps."):
                print("{} not downloaded".format(f["name"]))
                continue
            if utf8_path_exists(local_path) and utf8_isdir(local_path):
                shutil.rmtree(local_path)
            with open(local_path, "wb") as fh:
                _ = download(files_resource, f["id"], fh)
        pulled.append(local_path)

    return pulled


def list_folder(files_resource, folder_id):
    next_page_token = None
    files: typing.List[dict] = []
    query = "'{}' in parents".format(folder_id)

    while True:
        resp = files_resource.list(q=query, pageToken=next_page_token).execute()
        files += list(resp["files"])
        next_page_token = resp.get("nextPageToken")

        if next_page_token is None:
            break

    return files


def download(files_resource, file_id, fh):
    request = files_resource.get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return status.progress == 100
