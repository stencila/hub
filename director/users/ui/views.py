from allauth.account.views import (
    SignupView,
    LoginView,
    LogoutView
)
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import (
    AccessMixin, LoginRequiredMixin
)
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import reverse, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    FormView, TemplateView
)

from accounts.models import AccountUserRole
from projects.project_data import get_projects, FILTER_OPTIONS

from .forms import BetaTokenForm, UsernameForm, UserSignupForm


class BetaTokenRequiredMixin(AccessMixin):
    """Token required for signin and signup during beta testing phase."""

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
    """View for user to enter a beta token."""

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


class UserSettingsView(LoginRequiredMixin, TemplateView):
    """Dashboard of settings available to the user."""

    template_name = "users/settings.html"


class UserSignupView(SignupView):
    """Override allauth SignupView to custom URL and template name."""

    template_name = 'users/signup.html'
    form_class = UserSignupForm


class UserSigninView(LoginView):
    """Override allauth LoginView to custom URL and template name."""

    template_name = 'users/signin.html'


class UserSignoutView(LogoutView):
    """Override of allauth LogoutView to custom URL and template name."""

    template_name = 'users/signout.html'


class UsernameChangeView(LoginRequiredMixin, FormView):
    template_name = 'users/username_change.html'
    form_class = UsernameForm
    success_url = reverse_lazy('user_settings')

    def get_initial(self) -> dict:
        return {
            'username': self.request.user.username
        }

    def form_valid(self, form: UsernameForm) -> HttpResponse:
        self.request.user.username = form.cleaned_data['username']
        try:
            self.request.user.save()
        except IntegrityError:
            messages.error(self.request, "Username can not be changed to '{}' as it is already in use.".format(
                form.cleaned_data['username']))
            return redirect('user_change_username')

        messages.success(self.request, "Your username was changed to '{}'.".format(form.cleaned_data['username']))
        return super(UsernameChangeView, self).form_valid(form)


class UserDashboardView(LoginRequiredMixin, View):
    """User dashboard."""

    RESULTS_TO_DISPLAY = 5

    def get(self, request: HttpRequest, *args, **kwargs):
        project_fetch_result = get_projects(request.user, request.GET.get('filter'),
                                            UserDashboardView.RESULTS_TO_DISPLAY)

        account_roles = AccountUserRole.objects.filter(user=self.request.user).select_related('account')
        return render(request, 'users/dashboard.html', {
            'project_fetch_result': project_fetch_result,
            'account_roles': account_roles,
            'filter_options': FILTER_OPTIONS
        })
