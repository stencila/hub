from datetime import datetime
import time
from unittest import mock

from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework_jwt.serializers import jwt_encode_handler
import jwt

from general.testing import DatabaseTestCase
from users.api.views.tokens import generate_username, GOOGLE_ISS, GOOGLE_AUDS


def parse_date(date_string):
    return datetime.fromisoformat(date_string.replace("Z", "+00:00"))


class TestCase(DatabaseTestCase):
    def list(self):
        return self.client.get(reverse("api-tokens-list"))

    def create(self, data={}):
        return self.client.post(reverse("api-tokens-list"), data)

    def retrieve(self, token):
        return self.client.get(reverse("api-tokens-detail", kwargs={"token": token}))

    def destroy(self, token):
        return self.client.delete(reverse("api-tokens-detail", kwargs={"token": token}))


class TokenFlowTests(TestCase):
    """Test granting, verifying, refreshing, and revoking tokens."""

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

        # Retrieve (also refreshes)
        response = self.retrieve(token)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"] == user
        assert response.data["id"] == token[:8]
        assert parse_date(response.data["created"]) == created
        assert parse_date(response.data["expiry"]) > expiry

        response = self.destroy(token)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = self.retrieve(token)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_failure(self):
        response = self.create()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["message"] == "Authentication credentials were not provided."
        )

        response = self.create({"username": "foo"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["message"] == "Authentication credentials were not provided."
        )

        response = self.create({"username": "evil", "password": "hackz"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
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


class TokenCreateOpenIdTests(TestCase):
    """Test creating an authentication token using an OpenId token."""

    def create(self, claims):
        """Post a request with an OpenId token parameter."""
        return super().create({"openid": jwt_encode_handler(claims)})

    @staticmethod
    def verify_token(token, *args, **kwargs):
        """Mock: decodes but does not verify OpenId token."""
        return jwt.decode(token, None, False)

    def test_no_token(self):
        response = super().create()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
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
        response = self.create({"exp": time.time() + 10})
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

    def test_unverified_email(self):
        with mock.patch("google.oauth2.id_token.verify_token", self.verify_token):
            response = self.create({"iss": GOOGLE_ISS, "aud": GOOGLE_AUDS[0]})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Email address has not been verified"

    def test_existing_email(self):
        User.objects.create_user("pete", "pete@example.com")

        with mock.patch("google.oauth2.id_token.verify_token", self.verify_token):
            response = self.create(
                {
                    "iss": GOOGLE_ISS,
                    "aud": GOOGLE_AUDS[0],
                    "email_verified": True,
                    "email": "pete@example.com",
                }
            )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "pete"

        # Can use the returned API token
        response = self.retrieve(response.data["token"])
        assert response.status_code == status.HTTP_200_OK

    def test_new_email(self):
        with mock.patch("google.oauth2.id_token.verify_token", self.verify_token):
            response = self.create(
                {
                    "iss": GOOGLE_ISS,
                    "aud": GOOGLE_AUDS[0],
                    "email_verified": True,
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
