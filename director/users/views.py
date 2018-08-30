from allauth.account.views import (
    SignupView,
    LoginView,
    LogoutView
)
from django.conf import settings
from django.contrib.auth.mixins import (
    AccessMixin, LoginRequiredMixin
)
from django.shortcuts import reverse, redirect
from django.views.generic import (
    FormView, TemplateView
)

from .forms import BetaTokenForm


class BetaTokenRequiredMixin(AccessMixin):
    """
    Token required for signin and signup during
    beta testing phase
    """

    def get_login_url(self):
        return 'user_beta'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.GET.get('token') == settings.BETA_TOKEN:
                request.session['beta_token'] = request.GET['token']
            elif not request.session.get('beta_token') == settings.BETA_TOKEN:
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class BetaTokenView(FormView):
    """
    View for user to enter a beta token
    """

    template_name = 'beta_token.html'
    form_class = BetaTokenForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid() and form.cleaned_data['token'] == settings.BETA_TOKEN:
            request.session['beta_token'] = form.cleaned_data['token']
            url = request.GET.get('next', reverse('user_signin'))
            return redirect(url)
        else:
            form.add_error("token", "Incorrect token")
        return self.render_to_response(dict(form=form))


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """
    Dashboard of settings available to the user
    """

    template_name = "account/settings.html"


class AccountSignupView(BetaTokenRequiredMixin, SignupView):
    """
    Override of allauth SignupView to allow for custom
    URL and template name (and perhaps more later)
    """

    template_name = 'account/signup.html'


class AccountSigninView(BetaTokenRequiredMixin, LoginView):
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
