"""
Assign account roles to the test users.
"""

from django.contrib.auth.models import User
from django.conf import settings

from accounts.models import Account, AccountUserRole, AccountRole


def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    for user in User.objects.all():
        for account in Account.objects.all():
            AccountUserRole.objects.create(
              account=account,
              user=user,
              role=AccountRole.objects.order_by('?').first()
            )
