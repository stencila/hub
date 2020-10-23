import json
import os
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

from util.files import Files, file_info
from util.gapis import gdocs_service


def pull_gdoc(
    source: dict, path: Optional[str] = None, secrets: dict = {}, **kwargs
) -> Files:
    """
    Pull a Google Doc into a project.
    """
    doc_id = source.get("doc_id")
    assert doc_id, "A Google Doc id is required"

    gdoc = gdocs_service(secrets).documents().get(documentId=doc_id).execute()

    if not path:
        path = f"gdoc-{doc_id}"

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as file:
        file.write(json.dumps(gdoc, indent=2).encode("utf-8"))

    return {path: file_info(path, mimetype="application/vnd.google-apps.document")}
