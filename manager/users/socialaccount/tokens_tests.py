from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken

from manager.testing import DatabaseTestCase
from users.socialaccount.tokens import (
    Provider,
    get_user_social_token,
    get_user_social_tokens,
    refresh_user_access_token,
)


class TokensTestCase(DatabaseTestCase):
    def test_no_existing_token(self):
        """
        A user that does not yet have a token.
        """
        SocialApp.objects.get_or_create(provider=Provider.google.name)

        # First request
        refresh_user_access_token(self.ada, "Google", "new-access-token")

        token = get_user_social_token(self.ada, Provider.google)
        assert token.token == "new-access-token"
        assert token.token_secret == ""

        # Second request
        refresh_user_access_token(self.ada, "Google", "refreshed-access-token")

        token = get_user_social_tokens(self.ada)[Provider.google]
        assert token.token == "refreshed-access-token"

    def test_an_existing_refresh_token(self):
        """
        A user that has an existing refresh token.
        """
        app, created = SocialApp.objects.get_or_create(provider=Provider.twitter.name)
        account, created = SocialAccount.objects.get_or_create(
            user=self.bob, provider=Provider.twitter.name
        )
        SocialToken.objects.create(
            account=account,
            app=app,
            token="existing-access-token",
            token_secret="existing-refresh-token",
        )

        refresh_user_access_token(self.bob, "Twitter", "new-access-token")

        token = get_user_social_token(self.bob, Provider.twitter)
        assert token.token == "existing-access-token"
        assert token.token_secret == "existing-refresh-token"
