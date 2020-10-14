import json
import os
from typing import Dict, List

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

from util.files import file_info, Files


def pull_gdoc(source: dict, path: str, secrets: Dict = {}, **kwargs) -> Files:
    """
    Pull a Google Doc into a project.
    """
    assert source.get("doc_id"), "A document id is required"
    assert secrets.get(
        "access_token"
    ), """A Google access token is required. Please connect a Google account to your Stencila
 account at https://hub.stenci.la/me/social/connections/."""

    credentials = GoogleCredentials(
        access_token=secrets.get("access_token"),
        client_id=secrets.get("client_id"),
        client_secret=secrets.get("client_secret"),
        refresh_token=secrets.get("refresh_token"),
        token_expiry=None,
        token_uri="https://accounts.google.com/o/oauth2/token",
        user_agent="Stencila Hub Client",
    )
    docs_service = build("docs", "v1", credentials=credentials, cache_discovery=False)
    document = docs_service.documents().get(documentId=source.get("doc_id")).execute()

    with open(path, "wb") as file:
        file.write(json.dumps(document).encode("utf-8"))

    return {path: file_info(path, mimetype="application/vnd.google-apps.document")}
