"""Helper classes and functions for testing the API."""

from typing import Optional

import pytest
from django.shortcuts import reverse
from knox.models import AuthToken
from knox.settings import knox_settings
from rest_framework import test
from rest_framework.response import Response

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

    def setUp(self) -> None:
        """Set up the test fixtures."""
        for username in ("ada", "bob", "cam"):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(username, password=username)
            setattr(self, username, user)

            instance, token = AuthToken.objects.create(user=user)
            setattr(self, "{}_token".format(username), token)

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
