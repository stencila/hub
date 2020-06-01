from django.test import Client

from general.testing import DatabaseTestCase


class SignInTestCase(DatabaseTestCase):
    def test_redirect_after_sign_in(self):
        """
        Test that the next parameter in the SignIn URL is respected.

        While we can't do a "direct" test of this parameter without browser interaction, we can check that when
        supplied, the sign in form has a hidden input with the name `next` and the value from the URL. We can also check
        that when posting the signing with that form parameter the redirect is correct.
        """
        # without next parameter, we should not have the hidden next field in the HTML
        client = Client()
        resp = client.get("/me/signin/")
        self.assertNotIn(b'input type="hidden" name="next"', resp.content)

        # when posting, we get redirected to /
        login_resp = client.post("/me/signin/", {"login": "ada", "password": "ada"})

        # this is a bit fiddly since / redirects to /me/dashboard/
        self.assertRedirects(
            login_resp, "/", fetch_redirect_response=False, target_status_code=302
        )

        # with the `next` parameter, it should be rendered in the form
        client = Client()
        resp = client.get("/me/signin/?next=/test-redirect/")
        self.assertIn(
            b'input type="hidden" name="next" value="/test-redirect/', resp.content
        )

        # when posting, provide the `next` value that should be in the form
        login_resp = client.post(
            "/me/signin/",
            {"login": "ada", "password": "ada", "next": "/test-redirect/"},
        )

        # we'll get a 404 since this page doesn't exists but it's OK we just want to check the location
        self.assertRedirects(
            login_resp, "/test-redirect/", fetch_redirect_response=False
        )
