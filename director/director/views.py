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
