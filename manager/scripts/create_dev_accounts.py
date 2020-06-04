from django.conf import settings

from accounts.models import Account, AccountRole, AccountUser, Team
from users.models import User


def run(*args):
    """Create accounts for the development database."""
    # Ensure that this is only used in development
    assert settings.DEBUG

    first_three_users = User.objects.all()[:3]
    last_four_users = User.objects.order_by("-id").all()[:4]

    for name in ["stencila", "hapuku-university", "craigiburn-college", "acme-ltd"]:
        account = Account.objects.create(name=name)

        AccountUser.objects.create(
            account=account, user=last_four_users[1], role=AccountRole.MEMBER.name
        )
        AccountUser.objects.create(
            account=account, user=last_four_users[2], role=AccountRole.MANAGER.name
        )
        AccountUser.objects.create(
            account=account, user=last_four_users[3], role=AccountRole.ADMIN.name
        )

        a_team = Team.objects.create(account=account, name="a-team")
        a_team.members.set(first_three_users)

        b_team = Team.objects.create(account=account, name="b-team")
        b_team.members.set(last_four_users)
