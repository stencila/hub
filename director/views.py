from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View


class HomeView(View):

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('project_list'))
        else:
            return redirect(reverse('beta_token'))
