import re
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .auth import login_guest_user
from .storer import storers
from .models import Project, Cluster

class FrontPageView(TemplateView):
    template_name = 'index.html'

class SignInView(TemplateView):
    template_name = 'signin.html'

class OpenView(TemplateView):
    template_name = 'open.html'

    def get(self, request, address=None):

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

                response = Project.open(user=request.user, address=address)
                # Redirect?

        return super().get(self, request)

class GalleryView(ListView):
    template_name = 'gallery.html'
    model = Project

    def get_queryset(self):
        return Project.objects.filter(gallery=True)[:12]


