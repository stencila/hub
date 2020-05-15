import os

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials


class GoogleClient(object):
    def __init__(self, token):
        # The user token has been refreshed by the director if
        # necessary, so server credentials are not provided here.
        self.credentials = GoogleCredentials(
            token, None, None, None, None, None, "Stencila Hub Client",
        )

    def docs_resource(self):
        docs_service = build(
            "docs", "v1", credentials=self.credentials, cache_discovery=False
        )
        return docs_service.documents()
