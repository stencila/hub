from unittest import mock

from allauth.account.models import EmailAddress
from allauth.socialaccount import providers
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import (
    SocialAccount,
    SocialApp,
    SocialLogin,
    SocialToken,
)
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.client import RequestFactory


def mocked_requests_get(*args, **kwargs):
    class MockedResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] != "https://api.github.com/user/emails":
        return MockedResponse(None, 404)

    if "bad token" in kwargs["headers"]["Authorization"]:
        return MockedResponse(None, 400)

    if "token for bob1@example.com" in kwargs["headers"]["Authorization"]:
        return MockedResponse(
            [
                {"email": "bob@example.com", "verified": True, "primary": False},
                {"email": "bob1@example.com", "verified": True, "primary": True},
                {"email": "bob2@example.com", "verified": False, "primary": False},
                {"email": "geoffrey@example.com", "verified": True, "primary": False},
            ],
            200,
        )

    return MockedResponse(None, 404)


class SocialAccountAdapterTests(TestCase):
    def setUp(self):
        super(SocialAccountAdapterTests, self).setUp()
        site = Site.objects.get_current()
        for provider in providers.registry.get_list():
            app = SocialApp.objects.create(
                provider=provider.id,
                name=provider.id,
                client_id="app123id",
                key="123",
                secret="dummy",
            )
            app.sites.add(site)

    def _create_user(self, email="bob@example.com", verified=False):
        username = email.split("@")[0]
        user = User.objects.create(username=username, email=email)
        user.set_password("123")
        user.save()
        EmailAddress.objects.create(
            user=user, email=user.email, primary=True, verified=verified
        )
        return user

    def _create_social_user(self, emails, provider, uid, token=None):
        factory = RequestFactory()
        request = factory.get("/me/login/callback/")
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        MessageMiddleware().process_request(request)

        user = User(
            username=emails[0].email.split("@")[0],
            first_name=emails[0].email.split("@")[0],
            last_name=emails[0].email.split("@")[1],
            email=emails[0].email,
        )
        account = SocialAccount(provider=provider, uid=uid)

        if token is not None:
            token = SocialToken(
                token=token,
                account=account,
                app=SocialApp.objects.get(provider=provider),
            )

        sociallogin = SocialLogin(
            account=account, user=user, email_addresses=emails, token=token
        )
        complete_social_login(request, sociallogin)

    def test_different_email(self):
        # Base case: social login with an unknown email creates a new
        # user
        user = self._create_user(email="bob@example.com", verified=True)
        emails = [EmailAddress(email="bob1@example.com", verified=True, primary=True)]
        self._create_social_user(emails, "google", "10001")
        self.assertEqual(User.objects.count(), 2)
        socialaccount = SocialAccount.objects.get(uid="10001")
        self.assertTrue(socialaccount.user.id != user.id)

    def test_same_email_verified(self):
        # A social login matching an existing verified email attaches
        # to the existing user
        user = self._create_user(email="bob@example.com", verified=True)
        emails = [EmailAddress(email="bob@example.com", verified=True, primary=True)]
        self._create_social_user(emails, "google", "10001")
        self.assertEqual(User.objects.count(), 1)
        socialaccount = SocialAccount.objects.get(uid="10001")
        self.assertEqual(socialaccount.user.id, user.id)

    def test_same_email_unverified_1(self):
        # A social login matching an existing unverified email
        # does nothing (no auto-signup is allowed).
        self._create_user(email="bob@example.com", verified=False)
        emails = [EmailAddress(email="bob@example.com", verified=True, primary=True)]
        self._create_social_user(emails, "google", "10001")
        self.assertEqual(SocialAccount.objects.count(), 0)
        self.assertEqual(User.objects.count(), 1)

    def test_same_email_unverified_2(self):
        # A social login with an unverified email matching an existing
        # verified email does nothing (no auto-signup is allowed).
        self._create_user(email="bob@example.com", verified=True)
        emails = [EmailAddress(email="bob@example.com", verified=False, primary=True)]
        self._create_social_user(emails, "google", "10001")
        self.assertEqual(SocialAccount.objects.count(), 0)
        self.assertEqual(User.objects.count(), 1)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_github_auto_verified(self, mock_get):
        # A github login with an unverified email address is
        # automatically marked as verified.
        emails = [EmailAddress(email="bob1@example.com", verified=False, primary=True)]
        self._create_social_user(emails, "github", "10001", "(bad token)")
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(EmailAddress.objects.get(email="bob1@example.com").verified)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_github_unverified_match(self, mock_get):
        # A github login with an unverified email should match an
        # existing user with the same verified email.
        user = self._create_user(email="bob@example.com", verified=True)
        emails = [EmailAddress(email="bob@example.com", verified=False, primary=True)]
        self._create_social_user(emails, "github", "10001", "(bad token)")
        self.assertEqual(User.objects.count(), 1)
        socialaccount = SocialAccount.objects.get(uid="10001")
        self.assertEqual(socialaccount.user.id, user.id)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_github_secondary_email(self, mock_get):
        # A github user whose secondary email is verified, and matches
        # an existing verified email, should attach to the existing
        # user. Secondary github emails are imported unless they are
        # taken by some other existing user.
        bob = self._create_user(email="bob@example.com", verified=True)
        geoffrey = self._create_user(email="geoffrey@example.com", verified=True)

        emails = [EmailAddress(email="bob1@example.com", verified=True, primary=True)]
        self._create_social_user(
            emails, "github", "10001", "(token for bob1@example.com)"
        )

        socialaccount = SocialAccount.objects.get(uid="10001")
        self.assertEqual(socialaccount.user.id, bob.id)

        self.assertTrue(
            EmailAddress.objects.get(email="bob@example.com", user=bob.id).primary
        )
        self.assertTrue(
            EmailAddress.objects.get(email="bob1@example.com", user=bob.id).verified
        )
        self.assertFalse(
            EmailAddress.objects.get(email="bob1@example.com", user=bob.id).primary
        )
        self.assertFalse(
            EmailAddress.objects.get(email="bob2@example.com", user=bob.id).verified
        )
        self.assertFalse(
            EmailAddress.objects.filter(
                email="geoffrey@example.com", user=bob.id
            ).exists()
        )
        self.assertTrue(
            EmailAddress.objects.filter(
                email="geoffrey@example.com", user=geoffrey.id
            ).exists()
        )
