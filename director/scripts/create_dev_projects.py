"""
Create projects for the development database
"""

from django.conf import settings

from accounts.models import Account
from projects.models import Project


def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    # Assumes that there are at least 3 accounts
    accounts = Account.objects.all()

    Project.objects.create(
        account=accounts[0],
        public=True,
        name='The project name',
        description='''
The project description. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure 
dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non 
roident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        '''.strip()
    )

    Project.objects.create(
        account=accounts[1],
        public=True
    )

    Project.objects.create(
        account=accounts[2],
        public=False
    )
