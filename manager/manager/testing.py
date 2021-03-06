"""Helper classes and functions for testing the API."""

from typing import Optional

import pytest
from django.shortcuts import reverse
from knox.models import AuthToken
from knox.settings import knox_settings
from rest_framework import test
from rest_framework.response import Response

from accounts.models import Account, AccountTier
from projects.models.projects import Project
from users.models import User


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

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the test fixtures."""
        super().setUpClass()

        # Necessary, and not created when pytest `--nomigrations` option is used
        AccountTier.objects.create()
        Account.objects.create(name="stencila")
        Account.objects.create(name="temp")

        for username in ("ada", "bob", "cam"):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(username, password=username)
            setattr(cls, username, user)

            instance, token = AuthToken.objects.create(user=user)
            setattr(cls, "{}_token".format(username), token)

            public, _ = Project.objects.get_or_create(
                account=user.personal_account, creator=user, public=True, name="public",
            )
            setattr(cls, "{}_public".format(username), public)

            private, _ = Project.objects.get_or_create(
                account=user.personal_account,
                creator=user,
                public=False,
                name="private",
            )
            setattr(cls, "{}_private".format(username), private)

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

    @staticmethod
    def reverse(viewname_or_url: str, list_or_detail: str, kwargs={}) -> str:
        """Get the URL path for a view."""
        if viewname_or_url.startswith("/"):
            return viewname_or_url
        return reverse(
            viewname_or_url
            if "-" in viewname_or_url
            else f"api-{viewname_or_url}-{list_or_detail}",
            kwargs=kwargs,
        )

    def list(
        self, user: Optional[User], viewname: str, data={}, kwargs={}, headers={}
    ) -> Response:
        """List objects of a type for a user."""
        self.authenticate(user)
        return self.client.get(self.reverse(viewname, "list", kwargs), data, **headers)

    def create(
        self, user: Optional[User], viewname: str, data={}, kwargs={}, headers={}
    ) -> Response:
        """Create an object of a type for a user."""
        self.authenticate(user)
        return self.client.post(self.reverse(viewname, "list", kwargs), data, **headers)

    def retrieve(
        self, user: Optional[User], viewname: str, data={}, kwargs={}, headers={}
    ) -> Response:
        """Create an object of a type for a user."""
        self.authenticate(user)
        return self.client.get(
            self.reverse(viewname, "detail", kwargs), data, **headers,
        )

    def update(
        self, user: Optional[User], viewname: str, data={}, kwargs={}, headers={}
    ) -> Response:
        """Update an object of a type for a user."""
        self.authenticate(user)
        return self.client.patch(
            self.reverse(viewname, "detail", kwargs), data, **headers,
        )
