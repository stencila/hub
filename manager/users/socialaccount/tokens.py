from enum import Enum, unique
from typing import Dict, Optional, Tuple

from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth.models import User
from django.utils import timezone
from oauth2client import transport
from oauth2client.client import GoogleCredentials

from manager.api.exceptions import SocialTokenMissing


@unique
class Provider(Enum):
    """
    Enumeration of the social account providers used by the Hub.
    """

    github = "github"
    google = "google"
    orcid = "orcid"
    twitter = "twitter"

    @classmethod
    def has(cls, value: str):
        """Check if this enum has a value."""
        return value in cls._value2member_map_  # type: ignore


def get_user_social_token(
    user: User, provider: Provider, raise_exception: bool = False
) -> Optional[SocialToken]:
    """
    Get a social token for the user for a particular provider.
    """
    if raise_exception:
        token = get_user_social_token(user, provider)
        if token is None:
            message = (
                "To perform this action, you need to connect your {title} account: "
                "/me/{provider}/login/?process=connect"
            ).format(title=provider.name.title(), provider=provider.name)
            raise SocialTokenMissing({provider: message})
        else:
            return token

    if user.is_anonymous:
        return None

    return SocialToken.objects.filter(
        app__provider=provider.name, account__user=user
    ).first()


def get_user_google_token(
    user: User,
) -> Tuple[Optional[SocialToken], Optional[SocialApp]]:
    """
    Get a Google `SocialToken` for the user.

    If necessary will refresh the OAuth2 access token and
    update it in the database so that the refresh does not
    need to be done again within the next hour (at time of writing
    the expiry time for tokens).

    In most contexts that this function is used the Google `SocialApp`
    is also needed (e.g. for it's client_id etc) so we return that too.
    To avoid exceptions during development where there might not be a
    Google `SocialApp` we return None.
    """
    token = get_user_social_token(user, Provider.google)

    try:
        app = SocialApp.objects.get(provider=Provider.google.name)
    except SocialApp.DoesNotExist:
        app = None

    if token is None:
        return None, app

    # If the token has not expired just return it
    if token.expires_at is None or token.expires_at > timezone.now() - timezone.timedelta(
        seconds=90
    ):
        return token, app

    # The folowing are all required for a token refresh so if any
    # are missing, and the token has expired, return no token.
    if not (token.token and token.token_secret and token.expires_at):
        return None, app

    # Refresh the token
    credentials = GoogleCredentials(
        access_token=token.token,
        client_id=app.client_id,
        client_secret=app.secret,
        refresh_token=token.token_secret,
        token_expiry=token.expires_at,
        token_uri="https://accounts.google.com/o/oauth2/token",
        user_agent="Stencila Hub Client",
    )
    credentials.refresh(http=transport.get_http_object())
    info = credentials.get_access_token()

    # Save the new access token and expiry time
    token.token = info.access_token
    token.expires_at = timezone.now() + timezone.timedelta(seconds=info.expires_in)
    token.save()

    return token, app


def get_user_social_tokens(user: User) -> Dict[Provider, SocialToken]:
    """
    Get a dictionary of social tokens available for the user.
    """
    tokens = {}
    for provider in Provider:
        token = get_user_social_token(user, provider)
        if token:
            tokens[provider] = token
    return tokens


def refresh_user_access_token(user: User, provider: str, token: str):
    """
    Refresh the access token for a user for a provider.

    This will only update the access token if the user does not have an existing
    `SocialToken` with a refresh token (ie. if the user has not yet gone through
    the normal `allauth` flow).
    """
    provider = provider.strip().lower()

    # To avoid db queries go no further if this is not a known provider
    if not Provider.has(provider):
        return

    existing = SocialToken.objects.filter(
        account__user=user, app__provider=provider
    ).first()

    if existing:
        # If the existing token has a refresh token then do not update
        # (this may not be necessary but is being precautionary in case
        # overwriting the existing access token invalidates the refresh token)
        if existing.token_secret:
            return
        # Otherwise "refresh" the token using the supplied token
        else:
            existing.token = token
            existing.save()
    else:
        # Create a new social account and token for the user
        account, created = SocialAccount.objects.get_or_create(
            user=user,
            # Use our internal id here because we do not have one
            # one from the provider, and without it it is possible to
            # get a key violation error e.g. "(provider, uid)=(google, ) already exists".
            uid=f"stencila-user-{user.id}",
            provider=provider,
        )
        app = SocialApp.objects.get(provider=provider)
        SocialToken.objects.create(account=account, app=app, token=token)
