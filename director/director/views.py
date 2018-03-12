import re
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.generic import View, TemplateView, ListView
import allauth.account.views
from .auth import login_guest_user
from .forms import UserSignupForm, UserSigninForm
from .storer import storers
from .models import Project, Cluster


class FrontPageView(TemplateView):
    template_name = 'index.html'


class UserSignupView(allauth.account.views.SignupView):

    template_name = "user/signup.html"
    form_class = UserSignupForm


class UserSigninView(allauth.account.views.LoginView):

    template_name = "user/signin.html"
    form_class = UserSigninForm


class UserSignoutView(allauth.account.views.LogoutView):

    template_name = "user/signout.html"


class UserJoinView(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.email == 'guest':
            logout(request)
            return redirect('/me/signup/')
        else:
            return redirect('/')


class UserSettingsView(TemplateView):

    template_name = "user/settings.html"


class OpenInput(TemplateView):
    template_name = 'open-input.html'


class OpenAddress(TemplateView):
    template_name = 'open-address.html'

    def get(self, request, address=None):
        cluster = None
        token = None
        if address:
            try:
                proto, path = address.split("://")
                storer = storers[proto](path)
                assert(storer.valid_path())
                valid = True
            except:
                valid = False

            if valid:
                if not request.user.is_authenticated:
                    login_guest_user(request)

                cluster, token = Project.open(user=request.user, address=address)
        return self.render_to_response(dict(
            address=address,
            cluster=cluster,
            token=token
        ))


class GalleryView(ListView):
    template_name = 'gallery.html'
    model = Project

    def get_queryset(self):
        return Project.objects.filter(gallery=True)[:12]
