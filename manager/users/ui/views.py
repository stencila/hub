from allauth.account.views import LoginView, LogoutView, SignupView
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect as redir

from .forms import SignupForm


class SignupView(SignupView):
    """Override allauth SignupView to custom URL and template name."""

    template_name = "users/signup.html"
    form_class = SignupForm


class SigninView(LoginView):
    """Override allauth LoginView to custom URL and template name."""

    template_name = "users/signin.html"

    def get_context_data(self, *args, **kwargs):
        """Add extra context to template."""
        data = super().get_context_data(*args, **kwargs)
        data["providers"] = [
            dict(name="github", title="GitHub", icon="github"),
            dict(name="google", title="Google", icon="google"),
            dict(name="orcid", title="ORCID"),
            dict(name="twitter", title="Twitter", icon="twitter"),
        ]
        if "auth_provider" in self.request.COOKIES:
            data["auth_provider"] = self.request.COOKIES["auth_provider"]
        return data


class SignoutView(LogoutView):
    """Override of allauth LogoutView to custom URL and template name."""

    template_name = "users/signout.html"


@login_required
def redirect(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Redirect from unmatched /me URLs to the user's account.

    e.g. /me => /anna
    e.g. /me/settings -> /me/settings

    If user is unauthenticated, will be asked to signin first.
    """
    return redir("/{0}/{1}".format(request.user.personal_account, kwargs["rest"]))
