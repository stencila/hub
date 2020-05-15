import json
import os

from typing import List

from provider.google import GoogleClient


def pull_gdoc(source: dict, project: str, path: str) -> List[str]:
    """
    Pull google doc using given user token
    """
    assert "doc_id" in source, "source must have a doc_id"
    assert "token" in source, "source must include a token"

    gc = GoogleClient(source["token"])
    document = gc.docs_resource().get(documentId=source["doc_id"]).execute()

    with open(os.path.join(project, path), "wb") as file:
        file.write(json.dumps(document).encode("utf-8"))

    return [path]
