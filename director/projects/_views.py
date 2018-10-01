import json
import typing

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import HttpResponse, HttpRequest, QueryDict, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView

from users.views import BetaTokenRequiredMixin
from projects.view_base import DetailView, owner_access_check
from .models import SessionParameters
from .forms import (
    ProjectForm, get_initial_form_data_from_project, update_project_from_form_data, ProjectUpdateForm,
    ProjectAccessForm, ProjectSessionParametersForm, Project, ProjectSessionsForm, ProjectGeneralForm,
    update_general_project_data, update_session_parameters_project_data, update_access_project_data)


from .project_views import *


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


class ProjectDetailView(LoginRequiredMixin, DetailView):
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


class ProjectFormSaveView(DetailView):
    model = Project
    form_class: forms.Form

    def update_project(self, request: HttpRequest, project: Project, form: forms.Form) -> None:
        raise NotImplementedError("Subclasses must implement update_project method")

    def post(self, request: HttpRequest) -> HttpResponse:
        pk = request.POST.get('pk') or None
        project = self.get_instance(pk)

        if project is None:
            project = Project(creator=request.user)

        form = self.form_class(request.POST, initial=self.form_class.initial_data_from_project(project))
        form.helper.form_tag = False

        success = False

        if form.is_valid():
            success = True
            self.update_project(request, project, form)

        return self.build_response(project, form, success)

    @staticmethod
    def build_response(project: Project, form: forms.Form, success: bool) -> JsonResponse:
        return JsonResponse({
            'success': success,
            'errors': form.errors.get_json_data(),
            'project_id': project.pk,
            'project': {
                'key': project.key,
                'token': project.token
            }
        })


class ProjectGeneralSaveView(ProjectFormSaveView):
    form_class = ProjectGeneralForm

    def update_project(self, request: HttpRequest, project: Project, form: forms.Form) -> None:
        update_general_project_data(project, form.cleaned_data, True)


class ProjectSessionParametersSaveView(ProjectFormSaveView):
    form_class = ProjectSessionParametersForm

    def update_project(self, request: HttpRequest, project: Project, form: forms.Form) -> None:
        update_session_parameters_project_data(project, request, form.cleaned_data, form.cleaned_data, True)


class ProjectAccessSaveView(ProjectFormSaveView):
    form_class = ProjectAccessForm

    def update_project(self, request: HttpRequest, project: Project, form: forms.Form) -> None:
        update_access_project_data(project, form.cleaned_data, True)


class ProjectSessionsListView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int):
        project = get_object_or_404(Project, pk=pk)

        if not owner_access_check(request, project, "creator"):
            raise PermissionDenied

        return render(request, "projects/session_list.html", {"project": project})
