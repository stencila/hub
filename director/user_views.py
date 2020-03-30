from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from django.conf import settings
from accounts.models import AccountUserRole
from projects.project_data import get_projects, FILTER_OPTIONS

RESULTS_TO_DISPLAY = 5


class HomeView(View):
    """Home page view."""

    def get(self, request: HttpRequest, *args, **kwargs):
        # Send OK to Google's health checker which always hits /
        # despite sentings to the contrary.
        # This is a known bug being tracked here:
        # https://github.com/kubernetes/ingress-gce/issues/42
        # https://github.com/ory/k8s/issues/113#issuecomment-596281449
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'GoogleHC' in user_agent:
            return HttpResponse('OK')

        # Redirect to secure version. This needs to be done here to
        # avoid sending a 302 to GoogleHC.
        if settings.SECURE_SSL_REDIRECT and not request.is_secure():
            return redirect('https://' + request.get_host() + '/')

        if self.request.user.is_authenticated:
            project_fetch_result = get_projects(request.user, request.GET.get('filter'), RESULTS_TO_DISPLAY)

            account_roles = AccountUserRole.objects.filter(user=self.request.user).select_related('account')
            return render(request, 'users/dashboard.html', {
                'project_fetch_result': project_fetch_result,
                'account_roles': account_roles,
                'filter_options': FILTER_OPTIONS
            })
        else:
            return redirect(reverse('open_main'))
