import json
import os

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from typing import List

from .helpers import begin_pull, end_pull, Files


def pull_gdoc(source: dict, working_dir: str, path: str) -> Files:
    """
    Pull google doc using given user token.
    """
    assert source.get("doc_id"), "A document id is required"
    assert source.get("token"), "A Google authentication token is required"

    credentials = GoogleCredentials(
        source["token"], None, None, None, None, None, "Stencila Hub Client",
    )
    docs_service = build("docs", "v1", credentials=credentials, cache_discovery=False)
    document = docs_service.documents().get(documentId=source["doc_id"]).execute()

    temporary_dir = begin_pull(working_dir)
    with open(os.path.join(temporary_dir, path), "wb") as file:
        file.write(json.dumps(document).encode("utf-8"))
    files = end_pull(working_dir, path, temporary_dir)
    files[path]["mimetype"] = "application/vnd.google-apps.document"
    return files
