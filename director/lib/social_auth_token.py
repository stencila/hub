import typing

from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from django.contrib.auth.models import User


def user_social_token(user: User, provider_id: str) -> typing.Optional[SocialToken]:
    if user.is_anonymous:
        return None

    social_app = SocialApp.objects.filter(provider=provider_id).first()  # assume just one App with the ID is set up

    if social_app is None:
        return None

    social_account = SocialAccount.objects.filter(provider=provider_id, user=user).first()

    if social_account is None:
        return None

    return SocialToken.objects.filter(app=social_app, account=social_account).first()


def user_github_token(user: User) -> typing.Optional[str]:
    token = user_social_token(user, 'github')
    return token.token if token else None
