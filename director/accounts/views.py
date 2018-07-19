from allauth.account.views import (
    SignupView,
    LoginView,
    LogoutView
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin
)
from django.views.generic import (
    TemplateView
)


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """
    Dashboard of settings available to the user
    """

    template_name = "account/settings.html"


class AccountSignupView(SignupView):
    """
    Override of allauth SignupView to allow for custom
    URL and template name (and perhaps more later)
    """

    template_name = 'account/signup.html'


class AccountSigninView(LoginView):
    """
    Override of allauth LoginView to allow for custom
    URL and template name (and perhaps more later)
    """

    template_name = 'account/signin.html'


class AccountSignoutView(LogoutView):
    """
    Override of allauth LogoutView to allow for custom
    URL and template name (and perhaps more later)
    """

    template_name = 'account/signout.html'
