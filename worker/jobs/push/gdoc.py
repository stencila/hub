import json
import os
import tempfile

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import GoogleCredentials
from typing import List

from jobs.convert import Convert


def push_gdoc(paths: List[str], project: str, source: dict):
    """
    Push google doc using given user token
    """
    assert "doc_id" in source, "source must have a doc_id"
    assert "token" in source, "source must include a token"
    assert len(paths) == 1, "paths must contain exactly one item"

    docx = tempfile.NamedTemporaryFile(delete=False)
    convert = Convert()
    current = {}

    json_file = os.path.join(project, paths[0])

    convert.run(json_file, docx.name, {"from": "gdoc", "to": "docx"})

    credentials = GoogleCredentials(
        source["token"], None, None, None, None, None, "Stencila Hub Client",
    )
    drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    files_resource = drive_service.files()

    media = MediaFileUpload(docx.name)
    files_resource.update(fileId=source["doc_id"], media_body=media).execute()

    os.unlink(docx.name)
