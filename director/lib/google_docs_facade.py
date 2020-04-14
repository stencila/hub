import logging
import logging.handlers
import typing

import httplib2
from allauth.socialaccount.models import SocialToken
from django.utils import timezone
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client.client import GoogleCredentials

from projects.project_models import Project
from projects.source_models import GoogleDocsSource
from lib.path_operations import utf8_path_join

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

syslog_handler = logging.handlers.SysLogHandler()
syslog_handler.setLevel(logging.ERROR)
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)


class GoogleAuthHelper(object):
    client_id: str
    client_secret: str
    social_auth_token: typing.Optional[SocialToken]
    _credentials: typing.Optional[GoogleCredentials] = None

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        social_auth_token: typing.Optional[SocialToken] = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.social_auth_token = social_auth_token

    @property
    def auth_token_expired(self) -> bool:
        if self.social_auth_token is None:
            return False
        return (
            self.social_auth_token.expires_at is not None
            and self.social_auth_token.expires_at < timezone.now()
        )

    def build_credentials(self) -> typing.Optional[GoogleCredentials]:
        """Build a `GoogleCredentials` object from the `SocialToken`/client IDs we have."""
        if self.social_auth_token is None:
            return None

        return GoogleCredentials(
            self.social_auth_token.token,
            self.client_id,
            self.client_secret,
            self.social_auth_token.token_secret,
            self.social_auth_token.expires_at,
            GOOGLE_TOKEN_URI,
            "Stencila Hub Client",
        )

    @property
    def credentials(self) -> typing.Optional[GoogleCredentials]:
        if self._credentials is None:
            self._credentials = self.build_credentials()
        self.check_and_refresh_token(self._credentials)
        return self._credentials

    def update_social_auth_token(self, credentials: GoogleCredentials) -> None:
        """
        Store the new token and expiry date from a `GoogleCredentials` object.

        This is done after
        """
        if self.social_auth_token is None:
            return
        self.social_auth_token.token = credentials.access_token
        self.social_auth_token.expires_at = timezone.make_aware(
            credentials.token_expiry, timezone.utc
        )
        self.social_auth_token.save()

    def check_and_refresh_token(
        self, credentials: typing.Optional[GoogleCredentials]
    ) -> None:
        """Refresh the credentials (a `GoogleCredentials` object) from Google, if expired (according to us)."""
        if credentials is None or not self.auth_token_expired:
            return

        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)
        self.update_social_auth_token(credentials)


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
