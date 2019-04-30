import re

import httplib2
from allauth.socialaccount.models import SocialToken
from django.utils import timezone
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client.client import GoogleCredentials

from projects.project_models import Project
from projects.source_models import GoogleDocsSource
from projects.source_operations import utf8_path_join

GOOGLE_DOCUMENT_URL_FORMAT = 'https://docs.google.com/document/d/{}/edit'
GOOGLE_DOCUMENT_URL_RE = r'^(https://)?docs.google.com/document/d/([^/]+)/.*'


def build_google_document_url(document_id: str) -> str:
    return GOOGLE_DOCUMENT_URL_FORMAT.format(document_id)


def extract_google_document_id_from_url(url: str) -> str:
    url_match = re.match(GOOGLE_DOCUMENT_URL_RE, url)
    if url_match is None:
        raise ValueError('{} is not a Google Docs URL'.format(url))
    return url_match.group(2)


class GoogleAuthHelper(object):
    client_id: str
    client_secret: str
    social_auth_token: SocialToken
    _credentials: GoogleCredentials = None

    def __init__(self, client_id: str, client_secret: str, social_auth_token: SocialToken) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.social_auth_token = social_auth_token

    @property
    def auth_token_expired(self) -> bool:
        return self.social_auth_token.expires_at is not None and self.social_auth_token.expires_at < timezone.now()

    @property
    def credentials(self) -> GoogleCredentials:
        if self._credentials is None:
            self._credentials = GoogleCredentials(self.social_auth_token.token, self.client_id, self.client_secret,
                                                  self.social_auth_token.token_secret,
                                                  self.social_auth_token.expires_at,
                                                  GOOGLE_TOKEN_URI, 'Stencila Hub Client')
        return self._credentials

    def update_social_auth_token(self, credentials: GoogleCredentials) -> None:
        self.social_auth_token.token = credentials.access_token
        self.social_auth_token.expires_at = timezone.make_aware(credentials.token_expiry, timezone.utc)
        self.social_auth_token.save()

    def check_and_refresh_token(self) -> None:
        if not self.auth_token_expired:
            return
        http = self.credentials.authorize(httplib2.Http())
        self.credentials.refresh(http)
        self.update_social_auth_token(self.credentials)

    def get_credentials(self) -> GoogleCredentials:
        self.check_and_refresh_token()
        return self.credentials


class GoogleDocsFacade(object):
    client_id: str
    client_secret: str
    social_auth_token: SocialToken

    def __init__(self, client_id: str, client_secret: str, social_auth_token: SocialToken) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.social_auth_token = social_auth_token

    @property
    def credentials(self) -> GoogleCredentials:
        helper = GoogleAuthHelper(self.client_id, self.client_secret, self.social_auth_token)
        return helper.get_credentials()

    def get_document(self, document_id: str) -> dict:
        """"""
        docs_service = build('docs', 'v1', credentials=self.credentials, cache_discovery=False)
        docs_resource = docs_service.documents()

        return docs_resource.get(documentId=document_id).execute()

    def create_document_from_html(self, name: str, content: str) -> str:
        """Create a Google Doc from HTML and return its ID."""
        drive_service = build('drive', 'v3', credentials=self.credentials, cache_discovery=False)

        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.document'
        }

        document = MediaInMemoryUpload(content.encode('utf8'), mimetype='text/html', resumable=True)

        resp = drive_service.files().create(body=metadata, media_body=document, fields='id').execute()

        return resp['id']

    def create_source_from_document(self, project: Project, path: str, document_id: str) -> GoogleDocsSource:
        document_data = self.get_document(document_id)

        absolute_path = utf8_path_join(path, document_data['title'].replace('/', '_'))

        return GoogleDocsSource.objects.create(doc_id=document_id, project=project, path=absolute_path)

    def list_documents(self):
        drive_service = build('drive', 'v3', credentials=self.credentials, cache_discovery=False)

        resp = drive_service.files().list().execute()
        return resp
