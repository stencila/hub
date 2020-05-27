import typing
import httplib2

from allauth.socialaccount.models import SocialApp, SocialToken
from django.utils import timezone
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client.client import GoogleCredentials


class GoogleAuth(object):
    google_app: typing.Optional[SocialApp] = None
    social_auth_token: typing.Optional[SocialToken]
    _credentials: typing.Optional[GoogleCredentials] = None

    def __init__(self, social_auth_token: typing.Optional[SocialToken] = None,) -> None:
        self.social_auth_token = social_auth_token
        self.google_app = SocialApp.objects.filter(provider="google").first()

    def auth_token_expired(self):
        return (
            self.social_auth_token.expires_at is not None
            and self.social_auth_token.expires_at < timezone.now()
        )

    def init_credentials(self):
        """Build a `GoogleCredentials` object from the `SocialToken`/client IDs we have."""
        if self._credentials is not None:
            return

        self._credentials = GoogleCredentials(
            self.social_auth_token.token,
            self.google_app.client_id,
            self.google_app.secret,
            self.social_auth_token.token_secret,
            self.social_auth_token.expires_at,
            GOOGLE_TOKEN_URI,
            "Stencila Hub Client",
        )

    @property
    def credentials(self) -> typing.Optional[GoogleCredentials]:
        if self.social_auth_token is None:
            return None

        if self.google_app is None:
            return None

        self.check_and_refresh_token()
        return self._credentials

    def update_social_auth_token(self):
        self.social_auth_token.token = self._credentials.access_token
        self.social_auth_token.expires_at = timezone.make_aware(
            self._credentials.token_expiry, timezone.utc
        )
        self.social_auth_token.save()

    def check_and_refresh_token(self):
        """Refresh the credentials from Google, if expired (according to us)."""
        self.init_credentials()

        if not self.auth_token_expired():
            return self.social_auth_token.token

        http = self._credentials.authorize(httplib2.Http())
        self._credentials.refresh(http)
        self.update_social_auth_token()
        return self.social_auth_token.token
