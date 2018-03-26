import re
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView
import allauth.account.views
import io
import uuid
from .auth import login_guest_user
from .forms import UserSignupForm, UserSigninForm, CreateProjectForm
from .storer import Storer
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
                storer = Storer.get_instance_by_provider(proto)
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

    def post(self, request, address):
        # Address is a storer code, and the address components are in post variables
        try:
            storer = Storer.get_instance_by_provider(address)
        except:
            raise Http404
        form = storer.get_form(request.POST)
        if form.is_valid():
            return redirect('open', address=form.get_address())
        raise Http404

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

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectListView, self).get_context_data(*args, **kwargs)
        accounts = {a.provider: a for a in self.request.user.socialaccount_set.all()}
        enabled = []
        disabled = []
        providers = ['github', 'google']
        for provider in providers:
            account = accounts.get(provider, None)
            if account:
                enabled.append(Storer.get_instance_by_account(account))
            else:
                disabled.append(Storer.get_instance_by_provider(provider))
        context['storers'] = dict(enabled=enabled, disabled=disabled)
        return context

class StorerProjectBlock(TemplateView):
    template_name = 'storer_unit_list.html'

    def get_context_data(self):
        return dict(storer=self.storer, units=self.storer.units())

    def get(self, request, **kwargs):
        try:
            self.account = self.request.user.socialaccount_set.get(provider=kwargs['storer'])
            self.storer = Storer.get_instance_by_account(account=self.account)
        except Exception:
            raise Http404

        return self.render_to_response(self.get_context_data())

class StencilaProjectFileView(DetailView):
    model = StencilaProject

    def get(self, request, **kwargs):
        self.object = get_object_or_404(
            StencilaProject, owner__username=kwargs['user'], name=kwargs['project'])
        try:
            filename = kwargs['filename']
        except KeyError:
            raise Http404
        s = io.BytesIO()
        self.object.get_file(filename, s)
        response = HttpResponse(s.getvalue())
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

class StencilaProjectFilesBlock(DetailView):
    model = StencilaProject
    template_name = 'project_filelist_block.html'

    def get(self, request, **kwargs):
        self.object = get_object_or_404(
            StencilaProject, owner__username=kwargs['user'], name=kwargs['project'])
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

class StencilaProjectDetailView(DetailView):
    model = StencilaProject
    template_name = 'project_files.html'

    def get(self, request, **kwargs):
        self.object = get_object_or_404(
            StencilaProject, owner__username=kwargs['user'], name=kwargs['project'])
        context = self.get_context_data(
            object=self.object, owner=int(request.user == self.object.owner))
        return self.render_to_response(context)

class CreateProjectView(TemplateView):
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
            stencila_project = StencilaProject.get_or_create_for_user(self.request.user, uuid)
            stencila_project.upload(files)
            stencila_project.project.users.add(self.request.user)
            return redirect(
                'project-files',
                user=self.request.user.username,
                project=stencila_project.name)
        return self.render_to_response(dict(form=form))
