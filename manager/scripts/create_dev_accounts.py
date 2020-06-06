from django.conf import settings

from accounts.models import Account, AccountRole, AccountUser, Team
from users.models import User


def run(*args):
    """Create accounts for the development database."""
    # Ensure that this is only used in development
    assert settings.DEBUG

    user = User.objects.get(username="user")
    staff = User.objects.get(username="staff")
    admin = User.objects.get(username="admin")
    random_three_users = User.objects.order_by("?").all()[:3]

    for name in ["stencila", "hapuku-university", "craigiburn-college", "acme-ltd"]:
        account = Account.objects.create(name=name)

        AccountUser.objects.create(
            account=account, user=user, role=AccountRole.MEMBER.name
        )
        AccountUser.objects.create(
            account=account, user=staff, role=AccountRole.MANAGER.name
        )
        AccountUser.objects.create(
            account=account, user=admin, role=AccountRole.ADMIN.name
        )

        a_team = Team.objects.create(account=account, name="a-team")
        a_team.members.set([user, staff, admin])

        b_team = Team.objects.create(account=account, name="b-team")
        b_team.members.set(random_three_users)
