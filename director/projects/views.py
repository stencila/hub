import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    View,
    ListView,
    RedirectView,
    DetailView as DjangoDetailView
)
from django.views.generic.edit import (
    DeleteView,
    FormView
)

from projects.view_base import DetailView, owner_access_check
from .models import (
    Project,
    SessionParameters)
from .forms import (
    ProjectCreateForm,
    ProjectForm, get_initial_form_data_from_project, update_project_from_form_data, ProjectUpdateForm)


class ProjectListView(View):
    def get_project_queryset(self) -> QuerySet:
        if self.request.user.is_authenticated:
            return Project.objects.filter(
                Q(creator=self.request.user) | Q(public=True)
            )
        else:
            return Project.objects.filter(public=True)

    def get_session_parameters_queryset(self) -> QuerySet:
        if self.request.user.is_authenticated:
            return SessionParameters.objects.filter(owner=self.request.user)

        return SessionParameters.objects.none()

    def get(self, request) -> HttpResponse:
        projects = self.get_project_queryset()
        session_parameters = self.get_session_parameters_queryset()

        return render(request, "projects/project_list.html", {
            "projects": projects,
            "session_parameters": session_parameters
        })


class ProjectDetailView(DetailView):
    model = Project
    create_form_class = ProjectCreateForm
    edit_form_class = ProjectUpdateForm
    template = "projects/project_create.html"
    model_name = "Project"
    save_redirect_reverse = "project_list"

    def get_initial_instance(self, request: HttpRequest) -> Project:
        return Project(creator=self.request.user)

    def get_form_initial(self, request: HttpRequest, instance: typing.Optional[Project] = None) -> dict:
        return get_initial_form_data_from_project(instance)

    def form_post_create(self, request: HttpRequest, form: ProjectForm) -> None:
        form.populate_choice_fields(request.user)

    def update_and_save_instance(self, instance: Project, form: forms.Form):
        update_project_from_form_data(instance, form.cleaned_data)
        instance.save()

    def check_instance_ownership(self, instance: Project):
        if not (instance.public or owner_access_check(self.request, instance, 'creator')):
            raise PermissionDenied


class ProjectCreateView(LoginRequiredMixin, FormView):
    form_class = ProjectCreateForm
    template_name = 'projects/project_create.html'

    def get_success_url(self):
        return reverse('project_update', args=[self.project.id])

    def form_valid(self, form):
        self.project = Project.create(
            project_type=form.cleaned_data['type'],
            creator=self.request.user
        )
        return super().form_valid(form)


class ProjectReadView(LoginRequiredMixin, DjangoDetailView):
    model = Project
    fields = ['address']
    template_name = 'projects/project_read.html'


class ProjectUpdateView(LoginRequiredMixin, RedirectView):
    """
    Generic view for updating a project which redirects to
    the type-specific update view.
    """

    def get_redirect_url(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        return reverse('%s_update' % project.type, args=[kwargs['pk']])


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_delete.html'
    success_url = reverse_lazy('project_list')


class ProjectArchiveView(LoginRequiredMixin, View):
    @staticmethod
    def get(request: HttpRequest, pk: typing.Optional[int]) -> HttpResponse:
        project = get_object_or_404(Project, pk=pk)
        if not owner_access_check(request, project, "creator"):
            raise PermissionDenied

        archive = project.pull()
        body = archive.getvalue()

        response = HttpResponse(body, content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format('project.name')
        return response


class ProjectSessionsListView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int):
        project = get_object_or_404(Project, pk=pk)

        if not owner_access_check(request, project, "creator"):
            raise PermissionDenied

        return render(request, "projects/session_list.html", {"project": project})
