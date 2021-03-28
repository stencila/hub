from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class GasProvider(OAuth2Provider):
    """
    An OAuth2 provider for Google App Scripts.

    This needs to be a separate provider to the built in
    `GoogleProvider` because `allauth` only allows for one
    `SocialApp` per provider.
    """

    id = "gas"
    name = "Google App Scripts"
    account_class = ProviderAccount


provider_classes = [GasProvider]
