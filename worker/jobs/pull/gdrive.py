import os
import shutil
import typing
from typing import List

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from util.files import Files, file_info
from util.gapis import gdrive_service


def pull_gdrive(source: dict, path: str, secrets: dict = {}, **kwargs) -> Files:
    """
    Pull a Google Drive folder
    """
    assert source.get("kind") in (
        "file",
        "folder",
    ), "Kind is required and must be file or folder"
    assert source.get("google_id"), "A Google id is required"

    kind = source["kind"]
    google_id = source["google_id"]

    files_resource = gdrive_service(secrets).files()
    if kind == "file":
        return pull_file(files_resource, google_id, path)
    else:
        return pull_folder(files_resource, google_id, path)


def pull_file(files_resource, file_id: str, path: str) -> Files:
    """
    Pull a file from Google Drive.
    """
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)

    with open(path, "wb") as file:
        request = files_resource.get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

    return {path: file_info(path)}


def pull_folder(files_resource, folder_id: str, path: str) -> Files:
    """
    Pull a folder from Google Drive.
    """
    if os.path.exists(path):
        if not os.path.isdir(path):
            os.unlink(path)
    else:
        os.makedirs(path, exist_ok=True)

    files = {}
    for f in list_folder(files_resource, folder_id):
        child_path = os.path.join(path, f["name"])
        if f["mimeType"] == "application/vnd.google-apps.folder":
            files.update(pull_folder(files_resource, f["id"], child_path))
        else:
            if f["mimeType"].startswith("application/vnd.google-apps."):
                continue
            files.update(pull_file(files_resource, f["id"], child_path))
    return files


def list_folder(files_resource, folder_id: str):
    """
    List the files or sub-folders within a Google Drive folder.
    """
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
