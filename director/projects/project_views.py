import json
import typing
from datetime import datetime
from enum import Enum

from allauth.socialaccount.models import SocialApp
from django.conf import settings
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
from lib.google_docs_facade import GoogleDocsFacade
from lib.social_auth_token import user_github_token, user_social_token
from projects import parameters_presets
from projects.permission_facade import fetch_project_for_user, ProjectFetchResult
from projects.permission_models import ProjectPermissionType, ProjectRole, ProjectAgentRole, AgentType, \
    get_highest_permission, get_roles_under_permission
from projects.project_archiver import ProjectArchiver
from projects.project_puller import ProjectSourcePuller
from projects.source_models import Source, FileSource, LinkedSourceAuthentication
from projects.source_operations import list_project_virtual_directory, path_entry_iterator, \
    list_project_filesystem_directory, combine_virtual_and_real_entries, generate_project_archive_directory, \
    path_is_in_directory, utf8_scandir, utf8_isdir, utf8_realpath, utf8_path_join, utf8_path_exists, utf8_unlink, \
    to_utf8
from users.views import BetaTokenRequiredMixin
from .models import Project
from .project_forms import (
    ProjectCreateForm,
    ProjectSharingForm,
    ProjectSettingsMetadataForm,
    ProjectSettingsAccessForm,
    ProjectSettingsSessionsForm,
    ProjectArchiveForm)

User = get_user_model()

DEFAULT_ENVIRON = 'stencila/core'


class ProjectTab(Enum):
    FILES = 'files'


class ProjectPermissionsMixin(object):
    project_fetch_result: typing.Optional[ProjectFetchResult] = None
    project_permission_required: typing.Optional[ProjectPermissionType] = None

    @staticmethod
    def get_project_pk(url_kwargs: dict):
        return url_kwargs.get('project_pk', url_kwargs.get('pk'))

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.perform_project_fetch(request.user, self.get_project_pk(kwargs))
        self.test_required_project_permission()
        return super(ProjectPermissionsMixin, self).get(request, *args, **kwargs)  # type: ignore

    def post(self, request: HttpRequest, *args, **kwargs):
        self.perform_project_fetch(request.user, self.get_project_pk(kwargs))
        self.test_required_project_permission()
        return super(ProjectPermissionsMixin, self).post(request, *args, **kwargs)  # type: ignore

    def delete(self, request: HttpRequest, *args, **kwargs):
        self.perform_project_fetch(request.user, kwargs['pk'])
        self.test_required_project_permission()
        return super(ProjectPermissionsMixin, self).delete(request, *args, **kwargs)  # type: ignore

    def perform_project_fetch(self, user: AbstractUser, pk: int) -> None:
        if self.project_fetch_result is None:
            self.project_fetch_result = fetch_project_for_user(user, pk)

    def get_render_context(self, context: dict) -> dict:
        context['environ'] = DEFAULT_ENVIRON
        context['project'] = self.project
        context['project_roles'] = self.project_roles
        context['project_permissions'] = self.project_permissions
        return context

    def get_context_data(self, **kwargs) -> dict:
        context_data = super().get_context_data(**kwargs)  # type: ignore
        # this should only be used as a mixin to a view that will have the get_context_data function

        return self.get_render_context(context_data)

    def _test_project_fetch_result_set(self) -> None:
        if self.project_fetch_result is None:
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

    def get_project_puller(self, request: HttpRequest, pk: int) -> ProjectSourcePuller:
        self.perform_project_fetch(request.user, pk)

        self.test_required_project_permission()

        if not settings.STENCILA_PROJECT_STORAGE_DIRECTORY:
            raise RuntimeError('STENCILA_PROJECT_STORAGE_DIRECTORY setting must be set to pull Project files.')

        authentication = LinkedSourceAuthentication(user_github_token(request.user))

        return ProjectSourcePuller(self.project, settings.STENCILA_PROJECT_STORAGE_DIRECTORY, authentication, request)


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
            elif filter_key == 'shared':
                roles = ProjectAgentRole.filter_with_user_teams(user=request.user)
                all_projects = map(lambda par: par.project, roles)
                projects = filter(lambda proj: proj.creator != request.user, all_projects)
            elif filter_key == 'public':
                projects = Project.objects.filter(public=True)
            else:
                filter_key = 'created'
                projects = Project.objects.filter(creator=request.user)

            filter_options = (
                FilterOption('created', 'My Projects'),
                FilterOption('account', 'Account Projects'),
                FilterOption('shared', 'Projects Shared With Me'),
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
        """Pass the request through to the form so it can generate a set of accounts the user can use."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request

        if 'account_id' in self.request.GET:
            # set the initial account if passed in through a GET request (e.g. the link on the Account profile page)
            initial = kwargs.get('initial', {})
            initial['account'] = self.request.GET['account_id']
            kwargs['initial'] = initial

        return kwargs

    def form_valid(self, form):
        """If the project creation form is valid them make the current user the project creator."""
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

    def get_context_data(self, **kwargs):
        context = super(ProjectOverviewView, self).get_context_data(**kwargs)
        environ = {
            'NIXSTER': 'multi-mega'
        }.get(settings.EXECUTION_CLIENT, 'stencila/core')
        context['cloud_environ'] = environ
        return context


class ProjectFilesView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, pk: int, path: typing.Optional[str] = None) -> HttpResponse:  # type: ignore
        self.perform_project_fetch(request.user, pk)

        self.test_required_project_permission()

        authentication = LinkedSourceAuthentication(user_github_token(request.user))

        path = path or ''

        virtual_items = list_project_virtual_directory(self.project, path, authentication)
        on_disk_items = list_project_filesystem_directory(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, self.project,
                                                          path)

        directory_items = combine_virtual_and_real_entries(virtual_items, on_disk_items)

        session_check_path = reverse('session_queue_v1', args=(self.project.token,))
        session_start_path = reverse('session_start_v1', args=(self.project.token, DEFAULT_ENVIRON))

        return render(request, 'projects/project_files.html', self.get_render_context(
            {
                'session_check_path': session_check_path,
                'session_start_path': session_start_path,
                'linked_sources': list(self.project.sources.not_instance_of(FileSource)),
                'current_directory': path,
                'breadcrumbs': path_entry_iterator(path),
                'item_names': json.dumps([item.name for item in directory_items]),
                'items': directory_items,
                'inside_remote_source': False,
                'project_tab': ProjectTab.FILES.value
            })
                      )

    def post(self, request: HttpRequest, pk: int, path: typing.Optional[str] = None) -> HttpResponse:  # type: ignore
        self.perform_project_fetch(request.user, pk)
        if not self.has_permission(ProjectPermissionType.EDIT):
            raise PermissionDenied

        if request.POST.get('action') == 'unlink_source':
            source = self.get_source(request.user, pk, request.POST.get('source_id'))

            if isinstance(source, FileSource):
                raise TypeError("Can't unlink a File source")

            source_description = str(source)

            source.delete()

            messages.success(request, "'{}' was unlinked.".format(source_description))

        return redirect(request.path)


class ProjectPullView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        puller = self.get_project_puller(request, pk)
        puller.pull()
        return JsonResponse({'success': True})


class ProjectRefreshView(ProjectPermissionsMixin, View):
    """Load each project file from disk back into a FileSource."""

    project_permission_required = ProjectPermissionType.EDIT

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        self.perform_project_fetch(request.user, pk)
        self.test_required_project_permission()
        return render(request, 'projects/project_refresh.html')

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        return JsonResponse({'success': True})


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
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore  # doesn't match parent signature
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

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    messages.error(request, 'User "{}" does not exist.'.format(username))
                else:
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
                    messages.error(request, "Team with ID {} does not exist.".format(team_id))
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


class ProjectArchiveDownloadView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore  # doesn't match parent signature
        project = self.get_project(request.user, pk)

        archive = project.pull()
        body = archive.getvalue()

        response = HttpResponse(body, content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(project.name)
        return response


class ProjectDeleteView(ProjectPermissionsMixin, DeleteView):
    model = Project
    template_name = 'projects/project_delete.html'
    success_url = reverse_lazy('project_list')
    project_permission_required = ProjectPermissionType.MANAGE


class ArchivesDirMixin(object):
    @staticmethod
    def get_archives_directory(project: Project) -> str:
        return generate_project_archive_directory(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

    @staticmethod
    def get_archive_path(archives_directory, name) -> str:
        return utf8_realpath(utf8_path_join(archives_directory, name))


class ProjectArchiveView(ArchivesDirMixin, ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW
    template_name = 'projects/project_archives.html'

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore  # doesn't match parent signature
        project = self.get_project(request.user, pk)

        archives = self.list_archives(project)

        return render(request, self.template_name,
                      self.get_render_context({'archives': archives, 'form': ProjectArchiveForm()}))

    def list_archives(self, project: Project):
        archives_directory = self.get_archives_directory(project)
        if utf8_isdir(archives_directory):
            archives = map(lambda e: {
                'name': e.name.decode('utf8'),
                'size': e.stat().st_size,
                'created': datetime.fromtimestamp(e.stat().st_ctime)
            }, filter(lambda e: not e.name.startswith(b'.'),
                      sorted(
                          utf8_scandir(archives_directory), key=lambda e: e.stat().st_mtime, reverse=True)
                      )
                           )
        else:
            archives = []  # type: ignore
        return archives

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        self.project_permission_required = ProjectPermissionType.EDIT
        project = self.get_project(request.user, pk)

        if request.POST.get('action') == 'remove_archive':
            archive_name = request.POST.get('archive_name')

            if archive_name and archive_name != '.':
                archives_directory = self.get_archives_directory(project)
                archive_path = self.get_archive_path(archives_directory, archive_name)

                if not path_is_in_directory(archive_path, archives_directory):
                    raise PermissionDenied

                if utf8_path_exists(archive_path):
                    utf8_unlink(archive_path)
                    messages.success(request, 'Archive {} was deleted successfully.'.format(archive_name))
                else:
                    messages.warning(request, 'Archive {} does not exist.'.format(archive_name))

            return redirect(reverse('project_archives', args=(pk,)))

        form = ProjectArchiveForm(request.POST)

        if not form.is_valid():
            archives = self.list_archives(project)

            return render(request, self.template_name,
                          self.get_render_context({'archives': archives, 'form': form}))

        puller = self.get_project_puller(request, pk)

        archiver = ProjectArchiver(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project, puller)

        try:
            archiver.archive_project(form.cleaned_data['tag'])
        except Exception as e:
            messages.error(request, 'Archive failed: {}'.format(e))
        else:
            messages.success(request, 'Archive created successfully.')

        return redirect(reverse('project_archives', args=(pk,)))


class ProjectNamedArchiveDownloadView(ArchivesDirMixin, ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, pk: int, name: str) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk)

        archives_directory = self.get_archives_directory(project)
        archive_path = self.get_archive_path(archives_directory, name)

        if not path_is_in_directory(archive_path, archives_directory):
            raise PermissionDenied

        with open(to_utf8(archive_path), 'rb') as archive_file:
            response = HttpResponse(archive_file, content_type='application/x-zip-compressed')
            response['Content-Disposition'] = 'attachment; filename={}'.format(name)
            return response


class GdocsTest(View):

    def get(self, request):
        google_app = SocialApp.objects.filter(provider='google').first()

        gdf = GoogleDocsFacade(google_app.client_id, google_app.secret, user_social_token(request.user, 'google'))

        gdf.trash_document('104sCNP6wP-kTVuC61CEwSBt6eQAJyo66ydvm5RtRVkM')

        return HttpResponse('Hello')
