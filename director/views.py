from django.shortcuts import redirect
from django.urls import reverse

from accounts.views import BetaTokenView


class HomeView(BetaTokenView):
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
            return super().get(*args, **kwargs)
