from django.conf import settings

from accounts.models import Account, AccountRole, AccountTeam, AccountUser
from projects.models import Project
from users.models import User


def run(*args):
    """Create development database."""

    # Ensure that this is only used in development
    assert settings.DEBUG

    #################################################################
    # Users
    #################################################################

    # Admin (super user)
    admin = User.objects.create_user(
        username="admin",
        password="admin",
        first_name="Admin",
        email="admin@example.com",
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    # Staff member (not super user)
    staff = User.objects.create_user(
        username="staff",
        password="staff",
        first_name="Staff",
        email="staff@example.com",
    )
    staff.is_staff = True
    staff.save()

    # Normal users
    user = User.objects.create_user(
        username="user", password="user", first_name="User", email="user@example.com",
    )
    user.save()

    for spec in [
        ("joe", "Joe", "Blogs"),
        ("jane", "Jane", "Doe"),
        ("mike", "Mike", "Morris"),
        ("mary", "Mary", "Jones"),
    ]:
        User.objects.create_user(
            username=spec[0],
            password=spec[0],
            first_name=spec[1],
            last_name=spec[2],
            email=spec[0] + "@example.com",
        )

    #################################################################
    # Accounts
    #################################################################

    for name in ["stencila", "hapuku-university", "craigiburn-college", "acme-ltd"]:
        account = Account.objects.create(name=name)

        AccountUser.objects.create(
            account=account, user=user, role=AccountRole.MEMBER.name
        )
        AccountUser.objects.create(
            account=account, user=staff, role=AccountRole.MANAGER.name
        )
        AccountUser.objects.create(
            account=account, user=admin, role=AccountRole.OWNER.name
        )

        a_team = AccountTeam.objects.create(account=account, name="a-team")
        a_team.members.set([user, staff, admin])

        b_team = AccountTeam.objects.create(account=account, name="b-team")
        b_team.members.set(random_users(3))

    #################################################################
    # Projects
    #################################################################

    # Assumes that there are at least 3 accounts
    accounts = Account.objects.all()

    Project.objects.create(
        account=accounts[0],
        creator=random_account_user(accounts[0]),
        public=True,
        name="first-project",
        description="""
The project description. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut la
bore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex eacom
modo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. E
xcepteur sint occaecat cupidatat non roident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """.strip(),
    )

    Project.objects.create(
        name="second-project",
        account=accounts[1],
        creator=random_account_user(accounts[1]),
        public=True,
    )

    Project.objects.create(
        name="third-project",
        account=accounts[2],
        creator=random_account_user(accounts[2]),
        public=False,
    )


def random_users(num):
    return User.objects.order_by("?").all()[:num]


def random_account_user(account):
    return AccountUser.objects.filter(account=account).order_by("?").first().user
