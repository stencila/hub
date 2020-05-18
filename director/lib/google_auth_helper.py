import typing
import httplib2

from allauth.socialaccount.models import SocialApp, SocialToken
from django.utils import timezone
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client.client import GoogleCredentials

class GoogleAuthHelper(object):
    google_app: typing.Optional[SocialApp] = None
    social_auth_token: typing.Optional[SocialToken]
    _credentials: typing.Optional[GoogleCredentials] = None

    def __init__(
        self,
        social_auth_token: typing.Optional[SocialToken] = None,
    ) -> None:
        self.social_auth_token = social_auth_token
        self.google_app = SocialApp.objects.filter(provider="google").first()

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

        if self.google_app is None:
            return None

        return GoogleCredentials(
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
