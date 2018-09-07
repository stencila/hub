from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View


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


class Error500View(View):

    def get(self, *args, **kwargs):
        return render(self.request, '500.html')


class Test403View(View):
    """
    This view allows testing of 403 error handling in production
    (ie. that custom 403 page is displayed)
    """
    def get(self, request):
        raise PermissionDenied("This is a test 403 error")


class Test404View(View):
    """
    This view allows testing of 404 error handling in production
    (ie. that custom 404 page is displayed)
    """
    def get(self, request):
        raise Http404("This is a test 404 error")


class Test500View(View):
    """
    This view allows testing of 500 error handling in production (e.g that stack traces are
    being sent to Sentry)

    TODO Make sure this is only available for staff/admin https://django-braces.readthedocs.io/en/latest/access.html
    """
    def get(self, request):
        raise RuntimeError("This is a test error")
