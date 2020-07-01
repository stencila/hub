import logging

import invitations.views
from allauth.account.views import LoginView, LogoutView, SignupView
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect as redir
from django.shortcuts import reverse

from users.models import Invite

from .forms import SignupForm

logger = logging.getLogger(__name__)


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


class AcceptInviteView(invitations.views.AcceptInvite):
    """Override to allow for invite actions."""

    def get_object(self, *args, **kwargs):
        """
        Override to cache the invite instead of querying database twice.
        """
        if not hasattr(self, "invite"):
            self.invite = super().get_object(*args, **kwargs)
        return self.invite

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Override to perform invite action before or after sign up.
        """
        # Do the usual processing of the invite so that
        # it's `accepted` etc fields get updated
        super().post(request, *args, **kwargs)

        invite = self.get_object()
        if request.user.is_authenticated:
            # Perform the action now and redirect to it's URL
            invite.perform_action(request)
            return redir(invite.redirect_url())
        else:
            # Redirect to sign up page with invite URL
            # as next
            response = redir(
                reverse("ui-users-signup") + "?next=" + invite.redirect_url()
            )
            # Set a cookie so that the action is performed
            # once the user is logged in
            response.set_cookie("invite", invite.key)
            return response


def accept_invite_after_signup(sender, request, user, **kwargs):
    """
    Check for invite cookie and perform action if present.
    """
    key = request.COOKIES.get("invite")
    if not key:
        return

    try:
        invite = Invite.objects.get(key=key)
    except Invite.DoesNotExist:
        logger.warn("Could not find invite with key")
        return

    invite.perform_action(request, user)


signed_up_signal = (
    invitations.views.get_invitations_adapter().get_user_signed_up_signal()
)
signed_up_signal.connect(accept_invite_after_signup)


@login_required
def redirect(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Redirect from unmatched /me URLs to the user's account.

    e.g. /me => /anna
    e.g. /me/settings -> /me/settings

    If user is unauthenticated, will be asked to signin first.
    """
    return redir("/{0}/{1}".format(request.user.personal_account, kwargs["rest"]))
