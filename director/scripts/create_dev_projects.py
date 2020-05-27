"""
Create projects for the development database
"""

from django.conf import settings

from accounts.models import Account, AccountUserRole
from projects.models import Project


def random_account_member(account):
    return AccountUserRole.objects.filter(account=account).order_by("?").first().user


def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    # Assumes that there are at least 3 accounts
    accounts = Account.objects.filter(user=None)

    Project.objects.create(
        account=accounts[0],
        creator=random_account_member(accounts[0]),
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
        creator=random_account_member(accounts[1]),
        public=True,
    )

    Project.objects.create(
        name="third-project",
        account=accounts[2],
        creator=random_account_member(accounts[2]),
        public=False,
    )
