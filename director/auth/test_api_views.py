import time
from unittest import mock

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework_jwt.serializers import jwt_encode_handler
from rest_framework.test import APITestCase
import jwt

from auth.api_views import GrantView, GOOGLE_ISS, GOOGLE_AUDS


class TokenFlowTests(APITestCase):
    """Test granting, verifying, refreshing, and revoking tokens."""

    def test_uat(self):
        User.objects.create_user("sam", password="sam")
        response = self.client.post(
            reverse("api_auth_grant"), {"username": "sam", "password": "sam"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "sam"
        token = response.data["token"]

        # self.client.credentials(HTTP_AUTHORIZATION='UAT ' + token)
        # response = self.client.get(reverse("api_project_list"))
        # assert response.status_code == status.HTTP_200_OK

        response = self.client.post(reverse("api_auth_refresh"), {"token": token})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["token"] == token

        response = self.client.post(reverse("api_auth_verify"), {"token": token})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["token"] == token

        response = self.client.post(reverse("api_auth_revoke"), {"token": token})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["token"] is None

        response = self.client.post(reverse("api_auth_verify"), {"token": token})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["token"] is None

    def test_jwt(self):
        User.objects.create_user("jane", password="jane")
        response = self.client.post(
            reverse("api_auth_grant"),
            {"username": "jane", "password": "jane", "token_type": "jwt"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "jane"
        token = response.data["token"]

        response = self.client.post(reverse("api_auth_verify"), {"token": token})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["token"] == token

        response = self.client.post(reverse("api_auth_refresh"), {"token": token})
        assert response.status_code == status.HTTP_200_OK


class GrantViewOpenIdTests(APITestCase):
    """Test granting an authentication token using an OpenId token."""

    url = reverse("api_auth_grant")

    def post_token(self, claims, **kwargs):
        """Post a request with an OpenId token parameter."""
        data = {"openid": jwt_encode_handler(claims)}
        data.update(kwargs)
        return self.client.post(self.url, data)

    @staticmethod
    def verify_token(token, *args, **kwargs):
        """Mock: decodes but does not verify token."""
        return jwt.decode(token, None, False)

    def test_no_token(self):
        response = self.client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_bad_token(self):
        response = self.client.post(self.url, {"openid": "foo"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Bad token: Not enough segments"

    def test_token_expired(self):
        response = self.post_token({"exp": time.time() - 10})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Token has expired"

    def test_missing_issuer(self):
        response = self.post_token({"exp": time.time() + 10})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid token issuer"

    def test_invalid_issuer(self):
        response = self.post_token({"iss": "https://example.com"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid token issuer"

    def test_invalid_audience(self):
        response = self.post_token({"iss": GOOGLE_ISS, "aud": "foo"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid token audience"

    def test_unverified_email(self):
        with mock.patch("google.oauth2.id_token.verify_token", self.verify_token):
            response = self.post_token({"iss": GOOGLE_ISS, "aud": GOOGLE_AUDS[0]})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Email address has not been verified"

    def test_existing_email(self):
        User.objects.create_user("pete", "pete@example.com")

        with mock.patch("google.oauth2.id_token.verify_token", self.verify_token):
            response = self.post_token(
                {
                    "iss": GOOGLE_ISS,
                    "aud": GOOGLE_AUDS[0],
                    "email_verified": True,
                    "email": "pete@example.com",
                },
                token_type="jwt",
            )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "pete"

        token = response.data["token"]
        claims = self.verify_token(token)
        assert claims["username"] == "pete"

        # Can use the returned API token
        response = self.client.post(reverse("api_auth_verify"), {"token": token})
        assert response.status_code == status.HTTP_200_OK

    def test_new_email(self):
        with mock.patch("google.oauth2.id_token.verify_token", self.verify_token):
            response = self.post_token(
                {
                    "iss": GOOGLE_ISS,
                    "aud": GOOGLE_AUDS[0],
                    "email_verified": True,
                    "email": "mary@example.org",
                    "given_name": "Mary",
                    "family_name": "Morris",
                }
            )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "mary"

        user = User.objects.get(email="mary@example.org")
        assert user.username == "mary"
        assert user.first_name == "Mary"
        assert user.last_name == "Morris"

    def test_generate_username(self):
        gen = GrantView.generate_username

        assert gen(None, None, None) == "user-1"
        User.objects.create_user("user-1")

        assert gen(None, None, None) == "user-2"
        User.objects.create_user("user-2")

        assert gen(None, None, None) == "user-3"

        assert gen("joe@example.com", None, None) == "joe"
        User.objects.create_user("joe")

        assert gen("joe@example.org", None, None) == "joeexampleorg"
        User.objects.create_user("joeexampleorg")

        assert gen("joe@example.biz", "Joseph", None) == "joseph"
        User.objects.create_user("joseph")

        assert gen("joe@example.nz", "Joseph", "James") == "joseph-james"
        User.objects.create_user("joseph-james")

        assert gen("joe@example.us", "Joseph", "James") == "joeexampleus"
