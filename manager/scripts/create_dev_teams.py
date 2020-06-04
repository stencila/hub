from django.conf import settings

from accounts.models import Account, Team
from users.models import User


def run(*args):
    """Create teams for the development database."""
    # Ensure that this is only used in development
    assert settings.DEBUG

    for account in Account.objects.filter(name__in=["acme-ltd"]):
        ateam = Team.objects.create(account=account, name="a-team")
        ateam.members.set(User.objects.all()[:3])

        bteam = Team.objects.create(account=account, name="b-team")
        bteam.members.set(User.objects.order_by("-id").all()[:3])
