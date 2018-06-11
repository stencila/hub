import re
from allauth.socialaccount.models import SocialToken
from googleapiclient.discovery import build
from . import Storer

class GoogleStorer(Storer):
    code = 'google'
    name = 'Google'
    unit_name = 'drive folder'
    unit_name_plural = 'drive folders'

    def username(self):
        return self.account.extra_data.get('email')

    def units(self):
        return []
        # # scope https://www.googleapis.com/auth/drive.readonly
        # token = SocialToken.objects.get(account=self.account).token
        # drive_service = build('drive', 'v3', credentials=token)
        # response = drive_service.files().list(
        #     q="mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        #     fields='files(id, name)').execute()
