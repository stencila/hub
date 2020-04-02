import enum
import typing

from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from django.contrib.auth.models import User


class SocialAuthProviderId(enum.Enum):
    github = "github"
    google = "google"


def user_social_token(user: User, provider_id: str) -> typing.Optional[SocialToken]:
    if user.is_anonymous:
        return None

    social_app = SocialApp.objects.filter(
        provider=provider_id
    ).first()  # assume just one App with the ID is set up

    if social_app is None:
        return None

    social_account = SocialAccount.objects.filter(
        provider=provider_id, user=user
    ).first()

    if social_account is None:
        return None

    return SocialToken.objects.filter(app=social_app, account=social_account).first()


def user_github_token(user: User) -> typing.Optional[str]:
    token = user_social_token(user, "github")
    return token.token if token else None


def user_supported_social_providers(user: User) -> typing.Dict[str, bool]:
    """Get a dictionary of social providers supported by the user, in the form `{app_id: bool}`."""
    return {
        provider_id.value: user_social_token(user, provider_id.value) is not None
        for provider_id in SocialAuthProviderId
    }
