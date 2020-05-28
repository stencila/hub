from allauth.account.views import SignupView, LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from accounts.models import Account, AccountUserRole
from lib.constants import DISALLOWED_ACCOUNT_SLUGS
from projects.project_data import get_projects, FILTER_OPTIONS

from .forms import UsernameForm, UserSignupForm


class UserSettingsView(LoginRequiredMixin, TemplateView):
    """Dashboard of settings available to the user."""

    template_name = "users/settings.html"


class UserSignupView(SignupView):
    """Override allauth SignupView to custom URL and template name."""

    template_name = "users/signup.html"
    form_class = UserSignupForm


class UserSigninView(LoginView):
    """Override allauth LoginView to custom URL and template name."""

    template_name = "users/signin.html"


class UserSignoutView(LogoutView):
    """Override of allauth LogoutView to custom URL and template name."""

    template_name = "users/signout.html"


class UsernameChangeView(LoginRequiredMixin, FormView):
    template_name = "users/username_change.html"
    form_class = UsernameForm
    success_url = reverse_lazy("user_settings")

    def get_initial(self) -> dict:
        return {"username": self.request.user.username}

    def form_error(self, username, message=""):
        """Display form error message on validation error."""
        messages.error(
            self.request,
            (
                message
                if message != ""
                else "Username can not be changed to '{}' as it is already in use."
            ).format(username),
        )

    def form_valid(self, form: UsernameForm) -> HttpResponse:
        """
        Validate username change.

        Username is only valid if:

        - no other user is using the same name.
        - no organisation name is the same as the username.
        - does not match DISALLOWED_ACCOUNT_SLUGS
        """
        username = form.cleaned_data["username"]
        self.request.user.username = username

        if username in DISALLOWED_ACCOUNT_SLUGS:
            self.form_error(
                username,
                "Username can not be changed to '{}', this is a reserved name.",
            )
            return redirect("user_change_username")

        if Account.objects.filter(name=username).exists():
            self.form_error(username)
            return redirect("user_change_username")

        try:
            self.request.user.save()
        except IntegrityError:
            self.form_error(username)
            return redirect("user_change_username")

        messages.success(
            self.request, "Your username was changed to '{}'.".format(username),
        )

        return super(UsernameChangeView, self).form_valid(form)


class UserDashboardView(LoginRequiredMixin, View):
    """User dashboard."""

    RESULTS_TO_DISPLAY = 5

    def get(self, request: HttpRequest, *args, **kwargs):
        project_fetch_result = get_projects(
            request.user,
            request.GET.get("filter"),
            UserDashboardView.RESULTS_TO_DISPLAY,
        )

        account_roles = AccountUserRole.objects.filter(
            user=self.request.user
        ).select_related("account")
        return render(
            request,
            "users/dashboard.html",
            {
                "project_fetch_result": project_fetch_result,
                "account_roles": account_roles,
                "filter_options": FILTER_OPTIONS,
            },
        )
