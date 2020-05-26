"""Helper classes and functions for testing the API."""

from typing import Optional

from django.shortcuts import reverse
from knox.models import AuthToken
from knox.settings import knox_settings
from rest_framework import test
from rest_framework.response import Response
import pytest

from users.models import User
from accounts.models import Account, AccountPermission, AccountRole
from projects.models import Project, ProjectPermission, ProjectRole


def create_roles():
    """
    Create account and project roles.

    This is necessary only when running `pytest` with the `--nomigrations`
    option during local development (which is a lot faster) because these
    roles are created in
      - `accounts/migrations/0001_initial.py`
      - `projects/migrations/0005_auto_20180830_2324.py`
      - `accounts/migrations/0018_auto_20200426_1815.py`

    During testing on CI, `--no--migrations` is not used. Nonetheless,
    for the sake of test correctness, care should still be taken that these
    role definitions do not diverge from those used in prod databases.
    """
    account_roles = (
        ("member", ("modify", "view")),
        ("admin", ("modify", "administer", "view")),
        ("viewer", ("view",)),
    )
    for role_name, role_permissions in account_roles:
        role, created = AccountRole.objects.get_or_create(name=role_name)

        if not created:
            continue

        for permission_type in role_permissions:
            permission, created = AccountPermission.objects.get_or_create(
                type=permission_type
            )
            role.permissions.add(permission)

        role.save()

    project_roles = (
        ("Viewer", ("view",)),
        ("Reader", ("view", "comment")),
        ("Reviewer", ("view", "comment", "suggest")),
        ("Editor", ("view", "comment", "suggest", "edit")),
        ("Manager", ("view", "comment", "suggest", "edit", "manage")),
        ("Owner", ("view", "comment", "suggest", "edit", "manage", "own")),
    )
    for role_name, role_permissions in project_roles:
        role, created = ProjectRole.objects.get_or_create(name=role_name)

        if not created:
            continue

        for permission_type in role_permissions:
            permission, created = ProjectPermission.objects.get_or_create(
                type=permission_type
            )
            role.permissions.add(permission)

        role.save()


@pytest.mark.django_db
class DatabaseTestCase(test.APITestCase):
    """
    Base test case for tests that require database access.

    Does some basic scaffolding for test cases.
    Creates three users, `self.ada`, `self.bob` and `self.cam`.
    Each user has:
        - an authentication token e.g. `self.ada_token`
        - a personal account e.g. `self.ada_account`
        - two projects e.g. `self.ada_public`, `self.ada_private`

    You can use these to create further test fixture objects
    e.g. files within projects.

    Use the `create`, `retrieve` etc methods with the type of
    object and a username. e.g. `self.create("node", "ada", {...})`.
    The returned value is a `rest_framework.response.Response`.
    """

    def setUp(self) -> None:
        """Set up the test fixtures."""
        create_roles()

        for username in ("ada", "bob", "cam"):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(username, password=username)
            setattr(self, username, user)

            instance, token = AuthToken.objects.create(user=user)
            setattr(self, "{}_token".format(username), token)

            account = Account.objects.get(name="{}".format(username))
            setattr(self, "{}_account".format(username), account)

            public, _ = Project.objects.get_or_create(
                account=account,
                creator=user,
                public=True,
                name="{}-public-project".format(username),
            )
            setattr(self, "{}_public".format(username), public)

            private, _ = Project.objects.get_or_create(
                account=account,
                creator=user,
                public=False,
                name="{}-private-project".format(username),
            )
            setattr(self, "{}_private".format(username), private)

    def authenticate(self, user: Optional[User]) -> None:
        """
        Set authentication credentials for a user.

        If user is "anon" then an existing credentials are cleared.
        """
        if user is None:
            # Clear credentials
            self.client.credentials()
        else:
            token = getattr(self, "{}_token".format(user))
            self.client.credentials(
                HTTP_AUTHORIZATION="{} {}".format(
                    knox_settings.AUTH_HEADER_PREFIX, token
                )
            )

    def list(self, user: Optional[User], viewname: str, data={}, kwargs={}) -> Response:
        """List objects of a type for a user."""
        self.authenticate(user)
        return self.client.get(
            reverse(
                viewname if "-" in viewname else "api-{}-list".format(viewname),
                kwargs=kwargs,
            ),
            data,
        )

    def create(
        self, user: Optional[User], viewname: str, data={}, kwargs={}, headers={}
    ) -> Response:
        """Create an object of a type for a user."""
        self.authenticate(user)
        return self.client.post(
            reverse(
                viewname if "-" in viewname else "api-{}-list".format(viewname),
                kwargs=kwargs,
            ),
            data,
            **headers,
        )

    def retrieve(
        self, user: Optional[User], viewname: str, data={}, kwargs={}, headers={}
    ) -> Response:
        """Create an object of a type for a user."""
        self.authenticate(user)
        return self.client.get(
            reverse(
                viewname if "-" in viewname else "api-{}-detail".format(viewname),
                kwargs=kwargs,
            ),
            data,
            **headers,
        )


class AnonTestCase(DatabaseTestCase):
    """Tests when not authenticated."""

    username = "anon"


class AdaTestCase(DatabaseTestCase):
    """Tests when authenticated as test user Ada."""

    username = "ada"

    def setUp(self):
        super().setUp()
        self.client.login(username="ada", password="ada")


class BobTestCase(DatabaseTestCase):
    """Test when authenticated as test user Bob."""

    username = "bob"

    def setUp(self):
        super().setUp()
        self.client.login(username="bob", password="bob")


class CamTestCase(DatabaseTestCase):
    """Test when authenticated as test user Cam."""

    username = "cam"

    def setUp(self):
        super().setUp()
        self.client.login(username="cam", password="cam")
