import json
import os

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from typing import List


def pull_gdoc(source: dict, project: str, path: str) -> List[str]:
    """
    Pull google doc using given user token
    """
    assert "doc_id" in source, "source must have a doc_id"
    assert "token" in source, "source must include a token"

    credentials = GoogleCredentials(
        source["token"], None, None, None, None, None, "Stencila Hub Client",
    )
    docs_service = build("docs", "v1", credentials=credentials, cache_discovery=False)
    document = docs_service.documents().get(documentId=source["doc_id"]).execute()

    with open(os.path.join(project, path), "wb") as file:
        file.write(json.dumps(document).encode("utf-8"))

    return [path]
