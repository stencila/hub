import logging
import logging.handlers
import typing

from allauth.socialaccount.models import SocialToken
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from oauth2client.client import GoogleCredentials

from projects.project_models import Project
from projects.source_models import GoogleDocsSource
from lib.google_auth_helper import GoogleAuthHelper
from lib.path_operations import utf8_path_join

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

syslog_handler = logging.handlers.SysLogHandler()
syslog_handler.setLevel(logging.ERROR)
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)


class GoogleDocsFacade(object):
    _drive_service = None
    _auth_helper: GoogleAuthHelper

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        social_auth_token: typing.Optional[SocialToken] = None,
    ) -> None:
        self._auth_helper = GoogleAuthHelper(
            client_id, client_secret, social_auth_token
        )

    @property
    def credentials(self) -> typing.Optional[GoogleCredentials]:
        return self._auth_helper.credentials

    @property
    def drive_service(self):
        if self._drive_service is None:
            self._drive_service = build(
                "drive", "v3", credentials=self.credentials, cache_discovery=False
            )
        return self._drive_service

    def get_document(self, document_id: str) -> dict:
        """"""
        docs_service = build(
            "docs", "v1", credentials=self.credentials, cache_discovery=False
        )
        docs_resource = docs_service.documents()

        try:
            return docs_resource.get(documentId=document_id).execute()
        except Exception:
            logger.exception("Error getting document {}".format(document_id))
            raise

    def create_document(self, name: str, content: bytes, source_mimetype: str) -> str:
        """Create a Google Doc from a file and return its ID."""
        metadata = {"name": name, "mimeType": "application/vnd.google-apps.document"}

        document = MediaInMemoryUpload(
            content, mimetype=source_mimetype, resumable=True
        )

        resp = (
            self.drive_service.files()
            .create(body=metadata, media_body=document, fields="id")
            .execute()
        )

        return resp["id"]

    def create_source_from_document(
        self, project: Project, path: str, document_id: str
    ) -> GoogleDocsSource:
        document_data = self.get_document(document_id)

        absolute_path = utf8_path_join(path, document_data["title"].replace("/", "_"))

        return GoogleDocsSource(doc_id=document_id, project=project, path=absolute_path)

    def list_documents(self) -> typing.List[dict]:
        next_page_token = None
        files: typing.List[dict] = []
        while True:
            resp = self.drive_service.files().list(pageToken=next_page_token).execute()
            files += list(
                filter(
                    lambda f: f["mimeType"] == "application/vnd.google-apps.document",
                    resp["files"],
                )
            )
            next_page_token = resp.get("nextPageToken")

            if next_page_token is None:
                break

        return files

    def trash_document(self, document_id: str) -> None:
        self.drive_service.files().update(
            fileId=document_id, body={"trashed": True}
        ).execute()
