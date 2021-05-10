import base64
import time
from datetime import datetime
from unittest import mock

import jwt
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from knox.settings import knox_settings
from rest_framework import status

from manager.testing import DatabaseTestCase
from users.api.views.tokens import GOOGLE_AUDS, GOOGLE_ISS, generate_username


def parse_date(date_string):
    return datetime.fromisoformat(date_string.replace("Z", "+00:00"))


class TokenTestCase(DatabaseTestCase):
    """Base test case for testing token CRUD and authentication."""

    def authenticate(self, token, prefix=knox_settings.AUTH_HEADER_PREFIX):
        self.client.credentials(HTTP_AUTHORIZATION="{} {}".format(prefix, token))

    def unauthenticate(self):
        self.client.credentials()

    def list(self, token):
        self.authenticate(token)
        response = self.client.get(reverse("api-tokens-list"))
        self.unauthenticate()
        return response

    def create(self, data={}):
        return self.client.post(reverse("api-tokens-list"), data)

    def retrieve(self, token):
        return self.client.get(reverse("api-tokens-detail", kwargs={"token": token}))

    def destroy(self, token):
        return self.client.delete(reverse("api-tokens-detail", kwargs={"token": token}))


class TokenFlowTests(TokenTestCase):
    """Test granting, listing, refreshing, and revoking tokens."""

    def test_success(self):
        sam = User.objects.create_user("sam", password="sam")

        # Create
        response = self.create({"username": "sam", "password": "sam"})
        assert response.status_code == status.HTTP_201_CREATED

        user = response.data["user"]
        assert user == sam.pk
        assert response.data["username"] == "sam"

        token = response.data["token"]

        created = response.data["created"]
        expiry = response.data["expiry"]
        assert created <= timezone.now()
        assert expiry > timezone.now()

        # List
        response = self.list(token)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

        # Retrieve (also refreshes)
        response = self.retrieve(token)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"] == user
        assert response.data["id"] == token[:8]
        assert parse_date(response.data["created"]) == created
        assert parse_date(response.data["expiry"]) > expiry

        # Destroy
        response = self.destroy(token)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = self.retrieve(token)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_failure(self):
        response = self.create()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["message"] == "Authentication credentials were not provided."
        )

        response = self.create({"username": "foo"})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["message"] == "Authentication credentials were not provided."
        )

        response = self.create({"username": "evil", "password": "hackz"})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["message"] == "Incorrect authentication credentials."

        response = self.create({"openid": "bar"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Bad token: Not enough segments"

        response = self.retrieve("foo")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["message"] == "Not found."

        response = self.destroy("foo")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["message"] == "Not found."


def mock_verify_token(token, *args, **kwargs):
    """Mock: decodes but does not verify OpenId token."""
    return jwt.decode(token, options={"verify_signature": False})


def mock_verify_token_fail(*args, **kwargs):
    """Mock: simulate token verification failure."""
    raise ValueError


class TokenCreateOpenIdTests(TokenTestCase):
    """Test creating an authentication token using an OpenId token."""

    def create(self, claims):
        """Post a request with an OpenId token parameter."""
        defaults = {"iss": GOOGLE_ISS, "aud": GOOGLE_AUDS[0], "email_verified": True}
        defaults.update(claims)
        return super().create({"openid": jwt.encode(defaults, "not-a-secret")})

    def test_no_token(self):
        response = super().create()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["message"] == "Authentication credentials were not provided."
        )

    def test_bad_token(self):
        response = super().create({"openid": "foo"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Bad token: Not enough segments"

    def test_token_expired(self):
        response = self.create({"exp": time.time() - 10})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Token has expired"

    def test_missing_issuer(self):
        response = self.create({"iss": None})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Invalid token issuer"

    def test_invalid_issuer(self):
        response = self.create({"iss": "https://example.com"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Invalid token issuer"

    def test_invalid_audience(self):
        response = self.create({"iss": GOOGLE_ISS, "aud": "foo"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Invalid token audience"

    @mock.patch("google.oauth2.id_token.verify_token", mock_verify_token_fail)
    def test_verify_token_failure(self):
        response = self.create({})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Token could not be verified"

    @mock.patch("google.oauth2.id_token.verify_token", mock_verify_token)
    def test_unverified_email(self):
        response = self.create({"email_verified": False})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Email address has not been verified"

    @mock.patch("google.oauth2.id_token.verify_token", mock_verify_token)
    def test_existing_verified_email(self):
        pete = User.objects.create_user("pete")
        EmailAddress.objects.create(user=pete, email="pete@example.com", verified=True)

        response = self.create({"email": "pete@example.com"})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "pete"

        # Can use the returned API token
        response = self.retrieve(response.data["token"])
        assert response.status_code == status.HTTP_200_OK

    @mock.patch("google.oauth2.id_token.verify_token", mock_verify_token)
    @mock.patch("allauth.account.signals.email_confirmation_sent.send")
    def test_existing_unverified_email(self, send_mock):
        # User with email on `User` object
        janet = User.objects.create_user("janet", email="janet@example.org")

        response = self.create({"email": "janet@example.org"})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["message"]
            == "For security reasons, please verify your email address first; "
            "we have sent an email to janet@example.org."
        )
        assert send_mock.call_count == 1

        # Add a `EmailAddress` object that is unverified
        EmailAddress.objects.create(
            user=janet, email="janet@example.com", verified=False
        )

        response = self.create({"email": "janet@example.com"})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["message"]
            == "For security reasons, please verify your email address first; "
            "we have sent an email to janet@example.com."
        )
        assert send_mock.call_count == 2

    @mock.patch("google.oauth2.id_token.verify_token", mock_verify_token)
    def test_new_email(self):
        response = self.create(
            {
                "email": "mary@example.org",
                "given_name": "Mary",
                "family_name": "Morris",
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "mary"

        user = User.objects.get(email="mary@example.org")
        assert user.username == "mary"
        assert user.first_name == "Mary"
        assert user.last_name == "Morris"

    def test_generate_username(self):
        assert generate_username(None, None, None) == "user-1"
        User.objects.create_user("user-1")

        assert generate_username(None, None, None) == "user-2"
        User.objects.create_user("user-2")

        assert generate_username(None, None, None) == "user-3"

        assert generate_username("joe@example.com", None, None) == "joe"
        User.objects.create_user("joe")

        assert generate_username("joe@example.org", None, None) == "joeexampleorg"
        User.objects.create_user("joeexampleorg")

        assert generate_username("joe@example.biz", "Joseph", None) == "joseph"
        User.objects.create_user("joseph")

        assert generate_username("joe@example.nz", "Joseph", "James") == "joseph-james"
        User.objects.create_user("joseph-james")

        assert generate_username("joe@example.us", "Joseph", "James") == "joeexampleus"


class TokenAuthenticationTests(TokenTestCase):
    """Test authenticating with a token."""

    def me(self):
        return self.client.get(reverse("api-users-me"))

    def test_success(self):
        self.authenticate(self.ada_token)
        response = self.me()
        assert response.data["username"] == "ada"

        self.authenticate(self.bob_token)
        response = self.me()
        assert response.data["username"] == "bob"

        self.authenticate(base64.b64encode((self.cam_token).encode()).decode(), "Basic")
        response = self.me()
        assert response.data["username"] == "cam"

    def test_failure(self):
        self.authenticate("fake-token", "Token")
        response = self.me()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["message"] == "Invalid token."

        self.authenticate("", "Basic")
        response = self.me()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["message"]
            == "Invalid Basic authorization header. No credentials provided."
        )

        self.authenticate("too many parts", "Basic")
        response = self.me()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["message"]
            == "Invalid Basic authorization header. Credentials string should not contain spaces."
        )

        self.authenticate("//////", "Basic")
        response = self.me()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["message"]
            == "Invalid Basic authorization header. Credentials not correctly base64 encoded."
        )

        # Attempt to use username and password
        self.authenticate(
            base64.b64encode("username:password".encode()).decode(), "Basic"
        )
        response = self.me()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["message"]
            == "Basic authorization with a password is not allowed; use an API token instead."
        )

        self.authenticate(base64.b64encode("fake-token".encode()).decode(), "Basic")
        response = self.me()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["message"] == "Invalid token."
