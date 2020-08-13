import logging

import invitations.views
from allauth.account.views import LoginView, LogoutView, SignupView
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect as redir
from django.shortcuts import render, reverse

from users.api.serializers import InviteSerializer
from users.api.views.invites import InvitesViewSet
from users.models import Invite

logger = logging.getLogger(__name__)


class AuthenticationMixin:
    """Mixin to provide additional template context."""

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


class SignupView(AuthenticationMixin, SignupView):
    """Override allauth SignupView to custom URL and template name."""

    template_name = "users/signup.html"


class SigninView(AuthenticationMixin, LoginView):
    """Override allauth LoginView to custom URL and template name."""

    template_name = "users/signin.html"


class SignoutView(LogoutView):
    """Override of allauth LogoutView to custom URL and template name."""

    template_name = "users/signout.html"


@login_required
def invites_create(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Create a new invite.

    Will be linked to with action and arguments e.g

       /me/invites/send?email=user@example.com&action=join_account&account=3&next=/3
    """
    viewset = InvitesViewSet.init("create", request, args, kwargs)
    context = viewset.get_response_context()

    message = request.GET.get("message", "")
    action = request.GET.get("action")
    arguments = dict(
        [
            (key, value)
            for key, value in request.GET.items()
            if key not in ["email", "message", "action", "next"]
        ]
    )
    serializer = InviteSerializer(
        data=dict(message=message, action=action, arguments=arguments)
    )
    serializer.is_valid()

    next = request.GET.get("next", reverse("ui-users-invites-list"))

    return render(
        request,
        "invitations/create.html",
        dict(**context, serializer=serializer, next=next),
    )


@login_required
def invites_list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Get a list of invites.

    Mainly intended for users to be able to check to see what invites
    they have sent.
    """
    viewset = InvitesViewSet.init("list", request, args, kwargs)
    invites = viewset.get_queryset()
    return render(request, "invitations/list.html", dict(invites=invites))


class AcceptInviteView(invitations.views.AcceptInvite):
    """Override to allow for invite actions."""

    def get_object(self, *args, **kwargs):
        """
        Override to allow case sensitive matching of keys.
        """
        try:
            return Invite.objects.get(key=self.kwargs["key"])
        except Invite.DoesNotExist:
            return None

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Override to perform invite action before or after sign up.
        """
        # Do the usual processing of the invite so that
        # it's `accepted` etc fields get updated
        response = super().post(request, *args, **kwargs)
        invite = self.object

        if not invite:
            # No invite so just return response
            return response

        if request.user.is_authenticated:
            # Perform the action (if necessary) and redirect to it's URL
            if not invite.completed:
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
    After a user has signed up check for invite cookie and perform action if present.
    """
    key = request.COOKIES.get("invite")
    if not key:
        return

    try:
        invite = Invite.objects.get(key=key)
    except Invite.DoesNotExist:
        logger.warning("Could not find invite with key")
        return

    if not invite.completed:
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
