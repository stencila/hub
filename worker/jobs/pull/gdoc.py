import json
import os

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

from util.files import Files, file_info
from util.gapis import gdocs_service


def pull_gdoc(source: dict, path: str, secrets: dict = {}, **kwargs) -> Files:
    """
    Pull a Google Doc into a project.
    """
    assert source.get("doc_id"), "A Google Doc id is required"

    gdoc = (
        gdocs_service(secrets)
        .documents()
        .get(documentId=source.get("doc_id"))
        .execute()
    )

    with open(path, "wb") as file:
        file.write(json.dumps(gdoc, indent=2).encode("utf-8"))

    return {path: file_info(path, mimetype="application/vnd.google-apps.document")}
