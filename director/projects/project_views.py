import json
import typing

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View, CreateView, UpdateView, DetailView, DeleteView

from accounts.db_facade import fetch_accounts_for_user
from accounts.models import Team
from projects import parameters_presets
from projects.permission_facade import fetch_project_for_user, ProjectFetchResult
from projects.permission_models import ProjectPermissionType, ProjectRole, ProjectAgentRole, AgentType, \
    get_highest_permission, get_roles_under_permission
from projects.source_models import Source
from projects.source_operations import list_project_virtual_directory, path_entry_iterator
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

    @staticmethod
    def get_project_pk(url_kwargs: dict):
        return url_kwargs.get('project_pk', url_kwargs.get('pk'))

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.perform_project_fetch(request.user, self.get_project_pk(kwargs))
        self.test_required_project_permission()
        return super(ProjectPermissionsMixin, self).get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        self.perform_project_fetch(request.user, self.get_project_pk(kwargs))
        self.test_required_project_permission()
        return super(ProjectPermissionsMixin, self).post(request, *args, **kwargs)

    def delete(self, request: HttpRequest, *args, **kwargs):
        self.perform_project_fetch(request.user, kwargs['pk'])
        self.test_required_project_permission()
        return super(ProjectPermissionsMixin, self).delete(request, *args, **kwargs)

    def perform_project_fetch(self, user: AbstractUser, pk: int) -> None:
        if self.project_fetch_result is None:
            self.project_fetch_result = fetch_project_for_user(user, pk)

    def get_render_context(self, context: dict) -> dict:
        context['project'] = self.project
        context['project_roles'] = self.project_roles
        context['project_permissions'] = self.project_permissions
        return context

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        return self.get_render_context(context_data)

    def _test_project_fetch_result_set(self) -> None:
        if not self.project_fetch_result:
            raise ValueError("project_fetch_result not set")

    # mypy is told to ignore the return from these properties as it doesn't understand that
    # _test_project_fetch_result_set does a None check

    @property
    def project(self) -> Project:
        self._test_project_fetch_result_set()
        return self.project_fetch_result.project  # type: ignore

    @property
    def project_permissions(self) -> typing.Set[ProjectPermissionType]:
        self._test_project_fetch_result_set()
        return self.project_fetch_result.agent_permissions  # type: ignore

    @property
    def project_roles(self) -> typing.Set[ProjectRole]:
        self._test_project_fetch_result_set()
        return self.project_fetch_result.agent_roles  # type: ignore

    def has_permission(self, permission: ProjectPermissionType) -> bool:
        return self.has_any_permissions((permission,))

    def has_any_permissions(self, permissions: typing.Iterable[ProjectPermissionType]) -> bool:
        for permission in permissions:
            if permission in self.project_permissions:
                return True

        return False

    def test_required_project_permission(self) -> None:
        if self.project_permission_required is not None and not self.has_permission(self.project_permission_required):
            raise PermissionDenied

    def get_project(self, user: AbstractUser, project_pk: int) -> Project:
        self.perform_project_fetch(user, project_pk)
        self.test_required_project_permission()
        return self.project

    def get_source(self, user: AbstractUser, project_pk: int, source_pk: int) -> Source:
        self.perform_project_fetch(user, project_pk)
        self.test_required_project_permission()
        try:
            return self.project.sources.get(pk=source_pk)
        except Source.DoesNotExist:
            raise Http404

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
            filter_options: typing.Iterable[FilterOption] = []
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

        if 'account_id' in self.request.GET:
            # set the initial account if passed in through a GET request (e.g. the link on the Account profile page)
            initial = kwargs.get('initial', {})
            initial['account'] = self.request.GET['account_id']
            kwargs['initial'] = initial

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


class ProjectFilesView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, pk: int, path: typing.Optional[str] = None) -> HttpResponse:
        self.perform_project_fetch(request.user, pk)

        self.test_required_project_permission()

        directory_items = list_project_virtual_directory(self.project, path)

        return render(request, 'projects/project_files.html', self.get_render_context(
            {
                'current_directory': path or '',
                'breadcrumbs': path_entry_iterator(path),
                'items': directory_items
            })
                      )


class ProjectActivityView(ProjectPermissionsMixin, UpdateView):
    model = Project
    fields: typing.List[str] = []
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
        project_agent_roles = ProjectAgentRole.objects.filter(project=self.get_object()).order_by('content_type')
        # ordering by content_type SHOULD end up with Users first because it being a built in Django model should be
        # created before Team

        context_data['project_agent_roles'] = project_agent_roles
        context_data['project_agent_role_map'] = json.dumps({project_agent_role.pk: project_agent_role.role_id for
                                                             project_agent_role in project_agent_roles})

        context_data['all_roles'] = get_roles_under_permission(self.highest_permission)

        team_content_type = ContentType.objects.get_for_model(Team)

        context_data['user_content_type'] = ContentType.objects.get_for_model(User)
        context_data['team_content_type'] = team_content_type
        existing_teams = filter(lambda r: r.content_type == team_content_type, project_agent_roles)
        context_data['teams'] = Team.objects.filter(account=self.project.account).exclude(
            pk__in=map(lambda r: r.agent_id, existing_teams))

        return context_data


class ProjectRoleUpdateView(ProjectPermissionsMixin, LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.perform_project_fetch(request.user, pk)
        if not self.has_permission(ProjectPermissionType.MANAGE):
            raise PermissionDenied

        project_agent_role = None

        if request.POST.get('action') in ('set_role', 'remove_role'):
            project_agent_role = get_object_or_404(ProjectAgentRole, pk=request.POST['project_agent_role_id'])

        if project_agent_role and project_agent_role.agent_type == AgentType.USER and \
                project_agent_role.agent_id == request.user.pk:
            raise PermissionDenied  # user can not change their own access

        if request.POST.get('action') == 'remove_role':
            # mypy hint, only get here if project_agent_role is not None
            project_agent_role = typing.cast(ProjectAgentRole, project_agent_role)
            target_role = project_agent_role.role
        else:
            target_role = get_object_or_404(ProjectRole, pk=request.POST['role_id'])

        available_roles = get_roles_under_permission(self.highest_permission)

        if target_role not in available_roles:
            raise PermissionDenied  # user can not set/remove this role as it has permissions higher than what they have

        if request.POST.get('action') == 'remove_role':
            # mypy hint, only get here if project_agent_role is not None
            project_agent_role = typing.cast(ProjectAgentRole, project_agent_role)
            agent_description = project_agent_role.agent_description
            project_agent_role.delete()
            messages.success(request, "Access to the project was removed from {}".format(agent_description))
        elif request.POST.get('action') == 'set_role':
            project_agent_role = get_object_or_404(ProjectAgentRole, pk=request.POST['project_agent_role_id'])
            if project_agent_role.project != self.project:
                # user has permission on this Project but is trying to change the ProjectAgentRole on a different
                # Project
                raise PermissionDenied

            if project_agent_role.role != target_role:
                project_agent_role.role = target_role
                project_agent_role.save()
                return JsonResponse(
                    {'success': True, 'message': 'Access updated for {}'.format(project_agent_role.agent_description)})
        elif request.POST.get('action') in ('add_user_role', 'add_team_role'):
            content_type_class = None
            agent_id = None

            if request.POST['action'] == 'add_user_role':
                username = request.POST['name']

                if not username:
                    raise ValueError("Blank username provided")

                user = User.objects.get(username=username)

                if user == request.user:
                    messages.error(request, 'You can not alter your own access.')
                else:
                    agent_id = user.pk
                    content_type_class = User
            else:  # action == add_team_roles
                team_id = request.POST['team_id']
                try:
                    team = Team.objects.get(pk=team_id)
                except Team.DoesNotExist:
                    messages.error(request, "Team with PK {} does not exist.".format(team_id))
                else:
                    if team.account != self.project.account:
                        messages.error(request, "The selected Team does not belong to this account.")
                    else:
                        agent_id = team_id
                        content_type_class = Team

            if agent_id and content_type_class:
                project_agent_role, created = ProjectAgentRole.objects.update_or_create({
                    'role': target_role
                }, project=self.project, agent_id=agent_id,
                    content_type=ContentType.objects.get_for_model(content_type_class))
                messages.success(request,
                                 'Account access added for {}.'.format(project_agent_role.agent_description))

        return redirect(reverse('project_sharing', args=(self.project.id,)))


class ProjectSettingsView(ProjectPermissionsMixin, UpdateView):
    model = Project
    fields: typing.List[str] = []
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

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
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
