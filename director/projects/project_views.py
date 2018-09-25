import json
import typing

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import View, CreateView, UpdateView, DetailView, DeleteView

from accounts.db_facade import fetch_accounts_for_user
from accounts.models import Team
from projects import parameters_presets
from projects.permission_facade import fetch_project_for_user, ProjectFetchResult
from projects.permission_models import ProjectPermissionType, ProjectRole, ProjectAgentRole, AgentType, \
    get_highest_permission, get_roles_under_permission
from users.views import BetaTokenRequiredMixin
from .models import Project
from .project_forms import (
    ProjectCreateForm,
    ProjectSharingForm,
    ProjectSettingsMetadataForm,
    ProjectSettingsAccessForm,
    ProjectSettingsSessionsForm
)

User = get_user_model()


class ProjectPermissionsMixin(object):
    project_fetch_result: typing.Optional[ProjectFetchResult] = None
    project_permission_required: typing.Optional[ProjectPermissionType] = None

    def perform_project_fetch(self, user: User, pk: int) -> None:
        self.project_fetch_result = fetch_project_for_user(user, pk)

    def get_render_context(self, context: dict) -> dict:
        context['project_roles'] = self.project_roles
        context['project_permissions'] = self.project_permissions
        return context

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        return self.get_render_context(context_data)

    def _test_project_fetch_result_set(self) -> None:
        if not self.project_fetch_result:
            raise ValueError("project_fetch_result not set")

    @property
    def project(self) -> Project:
        self._test_project_fetch_result_set()
        return self.project_fetch_result.project

    @property
    def project_permissions(self) -> typing.Set[ProjectPermissionType]:
        self._test_project_fetch_result_set()
        return self.project_fetch_result.agent_permissions

    @property
    def project_roles(self) -> typing.Set[ProjectRole]:
        self._test_project_fetch_result_set()
        return self.project_fetch_result.agent_roles

    def has_permission(self, permission: ProjectPermissionType) -> bool:
        return self.has_any_permissions((permission,))

    def has_any_permissions(self, permissions: typing.Iterable[ProjectPermissionType]) -> bool:
        for permission in permissions:
            if permission in self.project_permissions:
                return True

        return False

    def get_project(self, user: User, project_pk: int) -> Project:
        self.perform_project_fetch(user, project_pk)

        if self.project_permission_required is not None and not self.has_permission(self.project_permission_required):
            raise PermissionDenied

        return self.project

    def get_object(self, *args, **kwargs):
        return self.get_project(self.request.user, self.kwargs['pk'])

    @property
    def highest_permission(self) -> typing.Optional[ProjectPermissionType]:
        return get_highest_permission(self.project_permissions)


class FilterOption(typing.NamedTuple):
    key: str
    label: str


class ProjectListView(BetaTokenRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            projects = Project.objects.filter(public=True)
            filter_key = 'public'
            filter_options = []
        else:
            filter_key = request.GET.get('filter')

            if filter_key == 'account':
                accounts = fetch_accounts_for_user(request.user)
                projects = Project.objects.filter(account__in=accounts)
            elif filter_key == 'public':
                projects = Project.objects.filter(public=True)
            else:
                filter_key = 'created'
                projects = Project.objects.filter(creator=request.user)

            filter_options = (
                FilterOption('created', 'My Projects'),
                FilterOption('account', 'Account Projects'),
                FilterOption('public', 'Public Projects')
            )

        return render(request, 'projects/project_list.html', {
            'object_list': projects,
            'filter_key': filter_key,
            'filter_options': filter_options
        })


class ProjectCreateView(LoginRequiredMixin, CreateView):
    form_class = ProjectCreateForm
    template_name = "projects/project_create.html"

    def get_form_kwargs(self):
        """
        Pass to request through to the form so it can generate
        a set of accounts the user can use
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """
        If the project creation form is valid them make the current user the
        project creator
        """
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        return reverse("project_overview", kwargs={'pk': self.object.pk})


class ProjectOverviewView(ProjectPermissionsMixin, DetailView):
    model = Project
    template_name = 'projects/project_overview.html'
    project_permission_required = ProjectPermissionType.VIEW


class ProjectFilesView(ProjectPermissionsMixin, UpdateView):
    model = Project
    fields = []
    template_name = 'projects/project_files.html'
    project_permission_required = ProjectPermissionType.VIEW


class ProjectActivityView(ProjectPermissionsMixin, UpdateView):
    model = Project
    fields = []
    template_name = 'projects/project_activity.html'
    project_permission_required = ProjectPermissionType.VIEW


class ProjectSharingView(ProjectPermissionsMixin, UpdateView):
    model = Project
    form_class = ProjectSharingForm
    template_name = 'projects/project_sharing.html'
    project_permission_required = ProjectPermissionType.MANAGE

    def get_success_url(self) -> str:
        return reverse("project_sharing", kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        project_agent_roles = ProjectAgentRole.objects.filter(project=self.get_object())
        context_data['project_agent_roles'] = project_agent_roles
        context_data['project_agent_role_map'] = json.dumps({project_agent_role.pk: project_agent_role.role_id for
                                                             project_agent_role in project_agent_roles})

        context_data['all_roles'] = get_roles_under_permission(self.highest_permission)
        context_data['user_content_type'] = ContentType.objects.get_for_model(User)
        context_data['team_content_type'] = ContentType.objects.get_for_model(Team)
        return context_data


class ProjectRoleUpdateView(ProjectPermissionsMixin, LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        self.perform_project_fetch(request.user, pk)
        if not self.has_permission(ProjectPermissionType.MANAGE):
            raise PermissionDenied

        if request.POST.get('action') == 'set_role':
            project_agent_role = get_object_or_404(ProjectAgentRole, pk=request.POST['project_agent_role_id'])
            if project_agent_role.project != self.project:
                # user has permission on this Project but is trying to change the ProjectAgentRole on a different
                # Project
                raise PermissionDenied

            new_role = get_object_or_404(ProjectRole, pk=request.POST['role_id'])

            available_roles = get_roles_under_permission(self.highest_permission)

            if new_role not in available_roles:
                raise PermissionDenied  # user can not set this role as it has permissions higher than what they have

            if project_agent_role.agent_type == AgentType.USER and project_agent_role.agent_id == request.user.pk:
                raise PermissionDenied  # user can not change their own access

            if project_agent_role.role != new_role:
                project_agent_role.role = new_role
                project_agent_role.save()
                return JsonResponse(
                    {'success': True, 'message': 'Access updated for {}'.format(project_agent_role.agent_description)})

        return JsonResponse({'success': False})


class ProjectSettingsView(ProjectPermissionsMixin, UpdateView):
    model = Project
    fields = []
    template_name = 'projects/project_settings.html'
    project_permission_required = ProjectPermissionType.MANAGE


class ProjectSettingsMetadataView(ProjectPermissionsMixin, UpdateView):
    model = Project
    form_class = ProjectSettingsMetadataForm
    template_name = 'projects/project_settings_metadata.html'
    project_permission_required = ProjectPermissionType.MANAGE

    def get_success_url(self) -> str:
        return reverse("project_settings_metadata", kwargs={'pk': self.object.pk})


class ProjectSettingsAccessView(ProjectPermissionsMixin, UpdateView):
    model = Project
    form_class = ProjectSettingsAccessForm
    template_name = 'projects/project_settings_access.html'
    project_permission_required = ProjectPermissionType.MANAGE

    def get_success_url(self) -> str:
        return reverse("project_settings_access", kwargs={'pk': self.object.pk})


class ProjectSettingsSessionsView(ProjectPermissionsMixin, UpdateView):
    model = Project
    form_class = ProjectSettingsSessionsForm
    template_name = 'projects/project_settings_sessions.html'
    project_permission_required = ProjectPermissionType.MANAGE

    def get_context_data(self, **kwargs):
        context_data = super(ProjectSettingsSessionsView, self).get_context_data(**kwargs)
        context_data['parameters_presets'] = json.dumps(parameters_presets.parameters_presets)
        return context_data

    def get_initial(self):
        return self.form_class.initial(self.object)

    def get_success_url(self) -> str:
        return reverse("project_settings_sessions", kwargs={'pk': self.object.pk})


class ProjectArchiveView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, pk: typing.Optional[int]) -> HttpResponse:
        project = self.get_project(request.user, pk)

        archive = project.pull()
        body = archive.getvalue()

        response = HttpResponse(body, content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format('project.name')
        return response


class ProjectDeleteView(ProjectPermissionsMixin, DeleteView):
    model = Project
    template_name = 'projects/project_delete.html'
    success_url = reverse_lazy('project_list')
    project_permission_required = ProjectPermissionType.MANAGE
