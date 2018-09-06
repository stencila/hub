from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View, TemplateView
from django.http import Http404


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

class Error404View(TemplateView):
    template_name = 'error404.html'

class Error500View(TemplateView):
    template_name = 'error500.html'

#TODO Make sure this is only available for logged in staff/admin
class Test500View(View):
    """

    """
    #TODO add constructor with the message that this is just a test
    def get(self, request):
        raise RuntimeError()
