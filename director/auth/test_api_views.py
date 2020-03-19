import time

from _pytest.monkeypatch import MonkeyPatch
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from rest_framework.test import APITestCase
import google.oauth2.id_token
import jwt

from auth.api_views import OpenIdGrantView, GOOGLE_ISS, GOOGLE_AUDS


class OpenIdGrantViewTests(APITestCase):

    url = reverse("api_openid_grant")

    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def post_token(self, claims):
        """Make a request payload with token"""
        return self.client.post(self.url, {"token": jwt_encode_handler(claims)})

    def mock_google_verify(self):
        self.monkeypatch.setattr(
            google.oauth2.id_token, "verify_token", self.verify_token
        )

    @staticmethod
    def verify_token(token, *args, **kwargs):
        """Mock: decodes but does not verify token"""
        return jwt.decode(token, None, False)

    def test_no_token(self):
        response = self.client.post(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bad_token(self):
        response = self.client.post(self.url, {"token": "foo"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == "Bad token: Not enough segments"

    def test_token_expired(self):
        response = self.post_token({"exp": time.time() - 10})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == "Token has expired"

    def test_missing_issuer(self):
        response = self.post_token({"exp": time.time() + 10})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == "Invalid token issuer"

    def test_invalid_issuer(self):
        response = self.post_token({"iss": "https://example.com"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == "Invalid token issuer"

    def test_invalid_audience(self):
        response = self.post_token({"iss": GOOGLE_ISS, "aud": "foo"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == "Invalid token audience"

    def test_unverified_email(self):
        self.mock_google_verify()
        response = self.post_token({"iss": GOOGLE_ISS, "aud": GOOGLE_AUDS[0]})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == "Email address has not been verified"

    def test_existing_email(self):
        User.objects.create_user("joe", "joe@example.com")

        self.mock_google_verify()
        response = self.post_token(
            {
                "iss": GOOGLE_ISS,
                "aud": GOOGLE_AUDS[0],
                "email_verified": True,
                "email": "joe@example.com",
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "joe"

        token = response.data["token"]
        claims = self.verify_token(token)
        assert claims["username"] == "joe"

        # Can use the returned API token
        response = self.client.post(reverse("api_token_verify"), {"token": token})
        assert response.status_code == status.HTTP_200_OK

    def test_new_email(self):
        self.mock_google_verify()
        response = self.post_token(
            {
                "iss": GOOGLE_ISS,
                "aud": GOOGLE_AUDS[0],
                "email_verified": True,
                "email": "mary@example.org",
                "given_name": "Mary",
                "family_name": "Morris"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "mary"

        user = User.objects.get(email="mary@example.org")
        assert user.username == "mary"
        assert user.first_name == "Mary"
        assert user.last_name == "Morris"

    def test_generate_username(self):
        gen = OpenIdGrantView.generate_username

        assert gen(None, None, None) == 'user1'
        User.objects.create_user("user1")
        
        assert gen(None, None, None) == 'user2'

        assert gen('joe@example.com', None, None) == 'joe'
        User.objects.create_user("joe")

        assert gen('joe@example.org', None, None) == 'joeexampleorg'
        User.objects.create_user("joeexampleorg")

        assert gen('joe@example.biz', "Joseph", None) == 'joseph'
        User.objects.create_user("joseph")

        assert gen('joe@example.nz', "Joseph", "James") == 'joseph-james'
