from enum import Enum, unique
from typing import Dict, Optional

from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth.models import User

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
