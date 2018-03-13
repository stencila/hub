import re
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import logout
from django.views.generic import View, TemplateView, ListView
import allauth.account.views
import boto3
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

class ProjectFileMixin(object):

    def s3_connection(self):
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    def list(self, prefix, bucket=settings.AWS_STORAGE_BUCKET_NAME):
        client = self.s3_connection()
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        contents = response.get('Contents', [])
        return [dict(
            name=c.get('Key', None),
            size=c.get('Size', None),
            last_modified=c.get('LastModified', None)) for c in contents]

class ProjectFiles(ProjectFileMixin, View):

    def get_user(self, request, **kwargs):
        return User.objects.get(username=kwargs['user'])

    def get_project(self, **kwargs):
        project_name = kwargs['project']
        prefix = "%s/%s" % (self.user.username, project_name)
        address = "hub://%s" % prefix
        return self.user.projects.get(address=address)

    def get_prefix(self, request, **kwargs):
        self.user = self.get_user(request, **kwargs)
        self.project = self.get_project(**kwargs)
        return "%s/%s" % (self.user.username, self.project)

    def get(self, request, **kwargs):
        try:
            prefix = self.get_prefix(request, **kwargs)
            listing = self.list(prefix)
        except Exception:
            return JsonResponse(dict(message="Not found"), status=404)
        return JsonResponse(dict(objects=listing), status=200)

class MyProjectFiles(ProjectFiles):

    def get_user(self, request, **kwargs):
        return self.request.user
