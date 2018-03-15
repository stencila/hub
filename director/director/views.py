import re
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.generic import View, TemplateView, ListView, CreateView
import allauth.account.views
import boto3
import uuid
from .auth import login_guest_user
from .forms import UserSignupForm, UserSigninForm, CreateProjectForm
from .storer import storers
from .models import Project, StencilaProject, Cluster

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
                storer = storers[proto]
                assert(storer.valid_path(path))
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

class ProjectListView(ListView):
    template_name = 'project_list.html'
    model = Project

    def get_queryset(self):
        return self.request.user.projects.all()

class ProjectFileStoreMixin(object):

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def s3_connection(self):
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    def list(self, prefix):
        client = self.s3_connection()
        response = client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        contents = response.get('Contents', [])
        return [dict(
            name=c.get('Key', None)[len(prefix):],
            size=c.get('Size', None),
            last_modified=c.get('LastModified', None)) for c in contents]

    def upload(self, prefix, files):
        client = self.s3_connection()
        for f in files:
            key = "%s/%s" % (prefix, f.name)
            client.upload_fileobj(f, self.bucket_name, key)

class ProjectFileArgsMixin(object):
    owner = None
    project = None

    def get_owner(self, **kwargs):
        if not self.owner:
            username = kwargs['user']
            self.owner = User.objects.get(username=username)
        return self.owner

    def get_project(self, **kwargs):
        if not self.project:
            self.project = self.get_owner(**kwargs).stencilaproject_set.get(
                name=kwargs['project']).project
        return self.project

class ProjectFilesData(ProjectFileStoreMixin, ProjectFileArgsMixin, View):

    def get_prefix(self, request, **kwargs):
        return str(self.get_project(**kwargs).stencilaproject.uuid) + '/'

    def get(self, request, **kwargs):
        try:
            prefix = self.get_prefix(request, **kwargs)
            listing = self.list(prefix)
        except Exception:
            return JsonResponse(dict(message="Not found"), status=404)
        return JsonResponse(dict(objects=listing), status=200)

class ProjectFilesView(ProjectFileStoreMixin, ProjectFileArgsMixin, TemplateView):
    template_name = 'project_files.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectFilesView, self).get_context_data(*args, **kwargs)
        context['project'] = dict(
            owner=self.get_owner(*args, **kwargs),
            project=self.get_project(*args, **kwargs))
        return context

class CreateProjectView(ProjectFileStoreMixin, TemplateView):
    template_name = 'project_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        if request.user.email == 'guest':
            logout(request)
            return redirect('user_signup')
        # TODO Check email address is verified
        return super(CreateProjectView, self).dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        context = dict(form=CreateProjectForm(), uuid=uuid.uuid4())
        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        form = CreateProjectForm(self.request.POST)
        files = self.request.FILES.getlist('file')
        uuid = self.request.POST.get('uuid')
        if form.is_valid():
            project = StencilaProject.get_or_create_for_user(self.request.user, uuid)
            self.upload(project.stencilaproject.uuid, files)
            project.users.add(self.request.user)
            return redirect(
                'project-files',
                user=self.request.user.username,
                project=project.stencilaproject.name)
        return self.render_to_response(dict(form=form))
