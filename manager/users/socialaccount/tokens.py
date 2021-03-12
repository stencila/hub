from enum import Enum, unique
from typing import Dict, Optional, Tuple

from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth.models import User
from django.db.models import Count
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


# A virtual `SocialApp` for Stencila's Google Apps Script OAuth Client
# This is necessary because `allauth` does not actually support
# multiple `SocialApps` for the same provider
# See https://github.com/pennersr/django-allauth/issues/1002
GAS = SocialApp(
    client_id="110435422451-kafa0mb5tt5c5nfqou4kussbnslfajbv.apps.googleusercontent.com"
)


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

    # Get a token for the user for the provider.
    # Note: a user may have more than one `SocialAccount` for the provider.
    # This does not differentiate between accounts
    # but rather prefers the token having a `token_secret` (a refresh token) and
    # one that expires the latest (ie. most recently added or refreshed)
    return (
        SocialToken.objects.filter(app__provider=provider.name, account__user=user)
        .annotate(has_refresh_token=Count("token_secret"))
        .order_by("-has_refresh_token", "-expires_at")
        .first()
    )


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

    # Here we need to spoof a separate `SocialApp` for the Google Apps Script
    # client by checking if the social account was created for `gas`
    account = token.account
    if (
        isinstance(account.extra_data, dict)
        and account.extra_data.get("social_app") == "gas"
    ):
        app = GAS

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


def refresh_user_access_token(user: User, social_app: str, token: str):
    """
    Refresh the OAuth access token for a user for a given social app.

    If the user does NOT already have a `SocialAccount` for the `SocialApp` then one will be added.
    If the `SocialAccount` already has a `SocialToken` WITHOUT a refresh token (i.e.
    one that was created by this function, rather than the normal `allauth` flow) then
    that token will be updated. Otherwise a new `SocialToken` will be created. The
    implementation is intended to do this but for efficiency sake (to reduce
    db queries) does things in a different order.
    """
    # All auth does not actually work with more than one `SocialApp` per
    # provider so we need to handle this here.
    provider = "google" if social_app == "gas" else social_app.lower()

    # See if the user has an existing token of this kind (ie without a refresh token)
    existing = SocialToken.objects.filter(
        account__user=user, app__provider__iexact=provider
    ).first()

    if existing:
        # If the existing token has a refresh token then do not update
        if existing.token_secret:
            return
        # Otherwise "refresh" the token using the supplied token
        else:
            existing.token = token
            existing.save()
    else:
        app = SocialApp.objects.get(provider=provider)

        # If the user already has an account with the _provider_ use that,
        # otherwise create a new account
        try:
            account = SocialAccount.objects.get(user=user, provider=app.provider)
        except SocialAccount.DoesNotExist:
            account = SocialAccount.objects.create(
                user=user,
                provider=app.provider,
                # Use our internal id here because we do not have one
                # one from the provider, and without it it is possible to
                # get a key violation error e.g. "(provider, uid)=(google, ) already exists".
                uid=user.id,
                # Indicate the social app that this was originally requested for
                extra_data=dict(social_app=social_app),
            )

        # Create the token
        SocialToken.objects.create(account=account, app=app, token=token)
