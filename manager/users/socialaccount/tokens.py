from enum import Enum, unique
from typing import Dict, Optional, Tuple

from allauth.socialaccount.models import SocialApp, SocialToken
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
    if token.expires_at > timezone.now() - timezone.timedelta(seconds=90):
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
