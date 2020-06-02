from allauth.account.views import LoginView, LogoutView, SignupView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import SignupForm, UsernameForm


class SettingsView(LoginRequiredMixin, TemplateView):
    """Dashboard of settings available to the user."""

    template_name = "users/settings.html"


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


class UsernameView(LoginRequiredMixin, FormView):
    """View to allow changing of username."""

    template_name = "users/username_change.html"
    form_class = UsernameForm
    success_url = reverse_lazy("ui-userS-settings")

    def get_initial(self) -> dict:
        """Get initial data for the form."""
        return {"username": self.request.user.username}

    def form_valid(self, form: UsernameForm):
        """Check that the entered username is valid."""
        self.request.user.username = form.cleaned_data["username"]
        try:
            self.request.user.save()
        except IntegrityError:
            messages.error(
                self.request,
                "Username can not be changed to '{}' as it is already in use.".format(
                    form.cleaned_data["username"]
                ),
            )
            return redirect("ui-users-username")

        messages.success(
            self.request,
            "Your username was changed to '{}'.".format(form.cleaned_data["username"]),
        )
        return super().form_valid(form)
