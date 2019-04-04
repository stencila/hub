import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, RedirectView

import _version
from lib.browser_detection import user_agent_is_internet_explorer
from lib.health_check import migrations_pending


class HomeView(View):
    """
    Home page view.

    Care needs to be taken that this view returns a 200 response (not a redirect)
    for unauthenticated users. This is because GCP load balancers ping the / path
    as a health check and will fail if anything other than a 200 is returned.
    """

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('project_list'))
        else:
            url = reverse('user_signin')
            token = self.request.GET.get('token')
            if token:
                url += '?token={}'.format(token)
            return redirect(url)


class StatusView(View):
    """A view that returns the current date for health checker purposes."""

    def get(self, request: HttpRequest) -> HttpResponse:
        if migrations_pending():
            return HttpResponse('Instance is not healthy: there are unapplied migrations.', status=500)

        resp = JsonResponse({
            'time': datetime.datetime.utcnow().isoformat(),
            'version': _version.__version__
        })
        resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        resp['Pragma'] = 'no-cache'
        resp['Expires'] = '0'
        return resp


class AboutView(TemplateView):
    """Page displaying short overview of the Hub."""

    template_name = 'about/about.html'


class ContactView(TemplateView):
    """Page displaying contact information."""

    template_name = 'about/contact.html'


class HelpView(TemplateView):
    """Page displaying help."""

    template_name = 'about/help.html'


class PrivacyView(TemplateView):
    """Page displaying the details of the Privacy Policy."""

    template_name = 'about/privacy.html'


class TermsView(TemplateView):
    """Page displaying the details of the Terms and Conditions."""

    template_name = 'about/terms-conditions.html'


class IcoView(RedirectView):
    permanent = True
    url = '/static/img/favicon.ico'


class Error500View(View):
    """
    Custom view to handling 500 error.

    A custom 500 view which pass the request into the template context
    so that the Sentry id is available for rendering.
    See https://docs.sentry.io/clients/python/integrations/django/
    """

    def get(self, *args, **kwargs):
        return TemplateResponse(self.request, '500.html', context={'request': self.request}, status=500)


class Test403View(View):
    """
    A 403 view to test 403 error.

    This view allows testing of 403 error handling in production
    (ie. test that custom 403 page is displayed)
    """

    def get(self, request):
        raise PermissionDenied("This is a test 403 error")


class Test404View(View):
    """
    A 404 view to test 404 error.

    This view allows testing of 404 error handling in production
    (ie. test that custom 404 page is displayed)
    """

    def get(self, request):
        raise Http404("This is a test 404 error")


class Test500View(View):
    """
    A 500 view to test 500 error.

    This view allows testing of 500 error handling in production (e.g that stack traces are
    being sent to Sentry). Can only be run by staff.
    """

    @method_decorator(staff_member_required)
    def get(self, request):
        raise RuntimeError("This is a test error")


class IeUnsupportedView(View):
    """A view to let users know that we don't support Internet Explorer (yet)."""

    def get(self, request: HttpRequest) -> HttpResponse:
        if not user_agent_is_internet_explorer(request.META.get('HTTP_USER_AGENT')):
            return redirect('/')

        return render(request, 'ie-unsupported.html')
