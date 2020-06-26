from typing import Dict, Optional

from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth.models import User

from manager.api.exceptions import SocialTokenMissing
from users.socialaccount.providers import ProviderId


def get_user_social_token(
    user: User, provider_id: ProviderId, raise_exception: bool = False
) -> Optional[SocialToken]:
    """
    Get a social token for the user for a particular provider.
    """
    if raise_exception:
        token = get_user_social_token(user, provider_id)
        if token is None:
            message = (
                "To perform this action, you need to connect your {title} account: "
                "/me/{provider}/login/?process=connect"
            ).format(title=provider_id.value.title(), provider=provider_id.value)
            raise SocialTokenMissing({provider_id.value: message})
        else:
            return token

    if user.is_anonymous:
        return None

    # Check there is a social app for the provider
    # Assume just one App with the ID is set up
    social_app = SocialApp.objects.filter(provider=provider_id).first()

    if social_app is None:
        return None

    # Check that the user has a social account for the provide
    social_account = SocialAccount.objects.filter(
        provider=provider_id, user=user
    ).first()

    if social_account is None:
        return None

    # Get the social token (if any)
    return SocialToken.objects.filter(app=social_app, account=social_account).first()


def get_user_social_tokens(user: User) -> Dict[ProviderId, SocialToken]:
    """
    Get a dictionary of social tokens available for the user.
    """
    tokens = {}
    for provider_id in ProviderId:
        token = get_user_social_token(user, provider_id)
        if token:
            tokens[provider_id] = token
    return tokens


def get_user_github_token(user: User) -> Optional[str]:
    """
    Get a user's Github token.
    """
    token = get_user_social_token(user, ProviderId.github)
    return token.token if token else None


def get_user_google_token(user: User) -> Optional[str]:
    """
    Get a user's Google token and refresh it if necessary.
    """
    # TODO: check and refresh if needed
    token = get_user_social_token(user, ProviderId.google)
    return token.token if token else None
