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
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        if 'GoogleHC' in user_agent:
            return HttpResponse('OK')

        if not settings.DEBUG and not request.is_secure():
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
            url = reverse('user_signin')
            token = self.request.GET.get('token')
            if token:
                url += '?token={}'.format(token)
            return redirect(url)
