import json
import os
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

from util.files import Files, ensure_parent, file_info
from util.gapis import gsheets_service


def pull_gsheet(
    source: dict, path: Optional[str] = None, secrets: dict = {}, **kwargs
) -> Files:
    """
    Pull a Google Sheet into a project.
    """
    doc_id = source.get("doc_id")
    assert doc_id, "A Google Sheet id is required"

    gsheet = (
        gsheets_service(secrets)
        .spreadsheets()
        .get(spreadsheetId=doc_id, includeGridData=True)
        .execute()
    )

    if not path:
        path = f"gsheet-{doc_id}"

    ensure_parent(path)

    with open(path, "wb") as file:
        file.write(json.dumps(gsheet, indent=2).encode("utf-8"))

    return {path: file_info(path, mimetype="application/vnd.google-apps.spreadsheet")}
