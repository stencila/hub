"""
Create accounts for the development database
"""

from django.conf import settings

from accounts.models import Account


def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    for account in [
        'hapuku-university',
        'craigiburn-college',
        'acme-ltd'
    ]:
        Account.objects.create(
            name=account,
        )
