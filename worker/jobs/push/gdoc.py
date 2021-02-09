import json
import os
import tempfile
from typing import List

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import GoogleCredentials

from jobs.convert import Convert


def push_gdoc(paths: List[str], project: str, source: dict):
    """
    Push google doc using given user token
    """
    assert "doc_id" in source, "source must have a doc_id"
    assert "token" in source, "source must include a token"
    assert len(paths) == 1, "paths must contain exactly one item"

    docx_file = tempfile.NamedTemporaryFile(delete=False).name
    json_file = os.path.join(project, paths[0])
    Convert().do(json_file, docx_file, {"from": "gdoc", "to": "docx"})  # type: ignore

    credentials = GoogleCredentials(
        source["token"], None, None, None, None, None, "Stencila Hub Client",
    )
    drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    files_resource = drive_service.files()

    media = MediaFileUpload(docx_file)
    files_resource.update(fileId=source["doc_id"], media_body=media).execute()

    os.unlink(docx_file)
