import json
import typing

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import HttpResponse, HttpRequest, QueryDict
from django.shortcuts import render, get_object_or_404, redirect
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
    ProjectForm, get_initial_form_data_from_project, update_project_from_form_data, ProjectUpdateForm,
    ProjectAccessForm, ProjectSessionParametersForm, ProjectGeneralForm, ProjectSessionsForm)


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


class FormContext(typing.NamedTuple):
    id: str
    name: str
    form: forms.Form
    is_base: bool = True


class ProjectGeneralFormContext(FormContext):
    form: ProjectGeneralForm


class ProjectSessionsFormContext(FormContext):
    form: ProjectSessionsForm


class ProjectSessionParametersFormContext(FormContext):
    form: ProjectSessionParametersForm


class ProjectAccessFormContext(FormContext):
    form: ProjectAccessForm


class ProjectForms(typing.NamedTuple):
    general: ProjectGeneralFormContext
    session_parameters: ProjectSessionParametersFormContext
    access: ProjectAccessFormContext
    sessions: ProjectSessionsFormContext


class ProjectDetailView(DetailView):
    model = Project
    create_form_class = ProjectCreateForm
    edit_form_class = ProjectUpdateForm
    template = "projects/project_detail.html"
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

    @staticmethod
    def get_system_session_parameters() -> QuerySet:
        return SessionParameters.objects.filter(is_system=True)

    def get_json_system_session_parameters(self) -> str:
        return json.dumps(list(map(lambda sp: sp.serialize(), self.get_system_session_parameters())))

    @staticmethod
    def get_forms(request: HttpRequest, project: typing.Optional[Project],
                  data: typing.Optional[QueryDict] = None) -> ProjectForms:
        general_form = ProjectGeneralForm(data, initial=ProjectGeneralForm.initial_data_from_project(project))
        general_form.helper.form_tag = False
        general_form.populate_source_choices(request)
        general_form_context = ProjectGeneralFormContext("general", "General", general_form)

        sessions_form = ProjectSessionsForm(data, initial=ProjectSessionsForm.initial_data_from_project(project))
        sessions_form.helper.form_tag = False
        sessions_form_context = ProjectSessionsFormContext("sessions", "Sessions", sessions_form, False)

        parameters_form = ProjectSessionParametersForm(data,
                                                       initial=ProjectSessionParametersForm.initial_data_from_project(
                                                           project))
        parameters_form.helper.form_tag = False
        parameters_form_context = ProjectSessionParametersFormContext("session-parameters", "Session Parameters",
                                                                      parameters_form)

        access_form = ProjectAccessForm(data, initial=ProjectAccessForm.initial_data_from_project(project))
        access_form.helper.form_tag = False
        access_form_context = ProjectAccessFormContext("access", "Access", access_form)

        return ProjectForms(
            general_form_context,
            parameters_form_context,
            access_form_context,
            sessions_form_context
        )

    def get_response(self, request: HttpRequest, project: typing.Optional[Project],
                     project_forms: ProjectForms) -> HttpResponse:
        return render(request, self.template, {
            'project': project,
            'forms': project_forms,
            'session_parameters': project.session_parameters if project else None,
            'system_session_parameters': self.get_json_system_session_parameters()
        })

    def get(self, request: HttpRequest, pk: typing.Optional[int] = None) -> HttpResponse:
        project = self.get_instance(pk)

        project_forms = self.get_forms(request, project)

        return self.get_response(request, project, project_forms)

    def post(self, request: HttpRequest, pk: typing.Optional[int] = None) -> HttpResponse:
        project = self.get_instance(pk)

        if project is None:
            project = Project(creator=request.user)

        project_forms = self.get_forms(request, project, request.POST)

        if all(map(lambda fc: fc.form.is_valid(), project_forms)):
            update_project_from_form_data(request, project, project_forms.general.form.cleaned_data,
                                          project_forms.sessions.form.cleaned_data,
                                          project_forms.session_parameters.form.cleaned_data,
                                          project_forms.access.form.cleaned_data)
            messages.success(request, "Project saved.")
            return redirect(reverse("project_update", args=(project.pk,)))
        else:
            messages.error(request, "Please correct all form errors to Save.")

        return self.get_response(request, project, project_forms)


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
