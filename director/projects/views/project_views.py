import json
import typing
from datetime import datetime
from enum import Enum

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.html import escape
from django.views.generic import View, CreateView, UpdateView, DetailView, DeleteView
from github import RateLimitExceededException

from accounts.db_facade import user_is_account_admin
from accounts.models import Team
from lib.resource_allowance import QuotaName, resource_limit_met, get_subscription_upgrade_text, \
    StorageLimitExceededException
from lib.social_auth_token import user_github_token, user_supported_social_providers
from projects import parameters_presets
from projects.permission_models import ProjectPermissionType, ProjectRole, ProjectAgentRole, AgentType, \
    get_roles_under_permission
from projects.project_archiver import ProjectArchiver
from projects.project_data import get_projects, FilterOption, FILTER_OPTIONS
from projects.source_models import Source, FileSource, LinkedSourceAuthentication, DiskSource
from projects.source_operations import list_project_virtual_directory, path_entry_iterator, \
    list_project_filesystem_directory, combine_virtual_and_real_entries
from lib.path_operations import to_utf8, utf8_isdir, utf8_path_exists, utf8_unlink, utf8_scandir, path_is_in_directory
from projects.views.mixins import ProjectPermissionsMixin, ArchivesDirMixin
from projects.models import Project
from projects.project_forms import (
    ProjectCreateForm,
    ProjectSharingForm,
    ProjectSettingsMetadataForm,
    ProjectSettingsAccessForm,
    ProjectSettingsSessionsForm,
    ProjectArchiveForm)
from projects.views.shared import DEFAULT_ENVIRON

User = get_user_model()


class ProjectTab(Enum):
    OVERVIEW = 'overview'
    FILES = 'files'
    FILES_CURRENT = 'current'
    FILES_ARCHIVES = 'archives'
    FILES_SNAPSHOTS = 'snapshots'
    ACTIVITY = 'activity'
    SHARING = 'sharing'
    SETTINGS = 'settings'
    SETTINGS_METADATA = 'metadata'
    SETTINGS_ACCESS = 'access'
    SETTINGS_SESSIONS = 'sessions'


class ProjectNamedRedirect(View):
    def get(self, request: HttpRequest, pk: int, path: typing.Optional[str] = None) -> HttpResponse:
        """Redirect old-style (id-based) URLs to new ones that use `name` as a slug."""
        project = get_object_or_404(Project, pk=pk)
        path = path or ''
        return redirect('/{}/{}/{}'.format(project.account.name, project.name, path), permanent=True)


class ProjectListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            filter_options: typing.Iterable[FilterOption] = []
        else:
            filter_options = FILTER_OPTIONS

        filter_option, projects, *_ = get_projects(request.user, request.GET.get('filter'))

        return render(request, 'projects/project_list.html', {
            'object_list': projects,
            'filter': filter_option,
            'filter_options': filter_options
        })


def project_save(form: ModelForm, saveable: typing.Union[ModelForm, Project]) -> bool:
    """Try to save the `saveable`, and handle the IntegrityError if raised."""
    try:
        saveable.save()
        return True
    except IntegrityError as e:
        # We have to assume that this is due to the project name not being unique
        if 'projects_project.name' in str(e):
            form.add_error('name',
                           'The Project name "{}" is already in use in this Account.'.format(form.cleaned_data['name']))
            return False
        raise


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
        """
        Check if the account to which the Project is assigned is allowed more Projects.

        If the project creation form is valid them make the current user the project creator.
        """
        account = form.cleaned_data['account']

        is_account_admin = user_is_account_admin(self.request.user, account)

        if resource_limit_met(account, QuotaName.MAX_PROJECTS):
            sub_upgrade_text = get_subscription_upgrade_text(is_account_admin, account)

            messages.error(self.request,
                           'A project can not be created for the Account <em>{}</em> as it has reached the quota of '
                           'Projects that its subscription allows. {}'.format(escape(account), sub_upgrade_text),
                           extra_tags='safe')
            return self.form_invalid(form)

        if not form.cleaned_data['public'] and resource_limit_met(account, QuotaName.MAX_PRIVATE_PROJECTS):
            sub_upgrade_text = get_subscription_upgrade_text(is_account_admin, account)
            messages.error(self.request,
                           'This Project must be made public as the subscription for the Account <em>{}</em> does not '
                           'allow private Projects. {}'.format(
                               escape(account), sub_upgrade_text), extra_tags='safe')
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.creator = self.request.user

        if not project_save(form, self.object):
            return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        return reverse('project_overview', args=(self.object.account.name, self.object.name))


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
        context['project_tab'] = ProjectTab.OVERVIEW.value
        return context


class ProjectFilesView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            path: typing.Optional[str] = None) -> HttpResponse:
        self.perform_project_fetch(request.user, account_name, project_name)

        self.test_required_project_permission()
        # TODO: Combine the above two lines into self.get_project?

        authentication = LinkedSourceAuthentication(user_github_token(request.user))

        path = path or ''

        try:
            virtual_items = list_project_virtual_directory(self.project, path, authentication)
            on_disk_items = list_project_filesystem_directory(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, self.project,
                                                              path)

            directory_items = combine_virtual_and_real_entries(virtual_items, on_disk_items)
        except RateLimitExceededException:
            directory_items = []
            sa_c_url = reverse('socialaccount_connections')
            messages.error(request, 'Could not list this directory as it contains Github sources and the anonymous '
                                    'rate limit has been exceeded.<br/>Please connect your Github account on the '
                                    '<a href="{}">Account Connections page</a> to remove this limit.'.format(sa_c_url),
                           extra_tags='safe')

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
                'project_tab': ProjectTab.FILES.value,
                'project_subtab': ProjectTab.FILES_CURRENT.value,
                'social_providers_supported': json.dumps(user_supported_social_providers(request.user))
            })
                      )

    def post(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
             path: typing.Optional[str] = None) -> HttpResponse:
        project = self.get_project(request.user, account_name, project_name)
        if not self.has_permission(ProjectPermissionType.EDIT):
            raise PermissionDenied

        if request.POST.get('action') == 'unlink_source':
            source_id = request.POST.get('source_id')

            if source_id:
                source = get_object_or_404(Source, project=project, pk=source_id)
            else:
                source = DiskSource()

            if isinstance(source, (FileSource, DiskSource)):
                raise TypeError("Can't unlink a File source")

            source_description = source.description

            source.delete()

            messages.success(request, "<em>{}</em> was unlinked.".format(escape(source_description)), extra_tags='safe')

        return redirect(request.path)


class ProjectPullView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def post(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        puller = self.get_project_puller(request, account_name, project_name)
        try:
            puller.pull()
        except StorageLimitExceededException:
            is_account_admin = user_is_account_admin(self.request.user, self.project.account)
            subscription_upgrade_text = get_subscription_upgrade_text(is_account_admin, self.project.account)

            messages.error(request,
                           'Could not pull the remote sources for this project, as it would exceed the storage limit '
                           'for the account <em>{}</em>. {}'.format(
                               escape(self.project.account), subscription_upgrade_text), extra_tags='safe'
                           )
            return JsonResponse({'success': False, 'reload': True})
        return JsonResponse({'success': True})


class ProjectActivityView(ProjectPermissionsMixin, UpdateView):
    model = Project
    fields: typing.List[str] = []
    template_name = 'projects/project_activity.html'
    project_permission_required = ProjectPermissionType.MANAGE

    def get_context_data(self, **kwargs) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data['project_tab'] = ProjectTab.ACTIVITY.value
        return context_data


class ProjectSharingView(ProjectPermissionsMixin, DetailView):
    model = Project
    form_class = ProjectSharingForm
    template_name = 'projects/project_sharing.html'
    project_permission_required = ProjectPermissionType.MANAGE

    def get_context_data(self, **kwargs) -> dict:
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

        context_data['project_tab'] = ProjectTab.SHARING.value

        return context_data


class ProjectRoleUpdateView(ProjectPermissionsMixin, LoginRequiredMixin, View):
    def post(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        self.perform_project_fetch(request.user, account_name, project_name)
        if not self.has_permission(ProjectPermissionType.MANAGE):
            raise PermissionDenied

        project_agent_role = None

        if request.POST.get('action') == 'set_public':
            self.project.public = request.POST['is_public'] == 'true' or \
                                  resource_limit_met(self.project.account, QuotaName.MAX_PRIVATE_PROJECTS)
            self.project.save()
            return JsonResponse({'success': True})

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

        return redirect('project_sharing', account_name, project_name)


class ProjectSettingsMetadataView(ProjectPermissionsMixin, UpdateView):
    model = Project
    form_class = ProjectSettingsMetadataForm
    template_name = 'projects/project_settings_metadata.html'
    project_permission_required = ProjectPermissionType.MANAGE

    def get_success_url(self) -> str:
        return reverse('project_settings_metadata', args=(self.object.account.name, self.object.name))

    def get_context_data(self, **kwargs):
        context_data = super(ProjectSettingsMetadataView, self).get_context_data(**kwargs)
        context_data['project_tab'] = ProjectTab.SETTINGS.value
        context_data['project_subtab'] = ProjectTab.SETTINGS_METADATA.value
        return context_data

    def form_valid(self, form: ModelForm):
        """If the form is valid, save the associated model."""
        if project_save(form, form):
            return super().form_valid(form)
        return super().form_invalid(form)


class ProjectSettingsAccessView(ProjectPermissionsMixin, UpdateView):
    model = Project
    form_class = ProjectSettingsAccessForm
    template_name = 'projects/project_settings_access.html'
    project_permission_required = ProjectPermissionType.MANAGE

    def get_success_url(self) -> str:
        return reverse('project_settings_access', args=(self.object.account.name, self.object.name))

    def get_context_data(self, **kwargs):
        context_data = super(ProjectSettingsAccessView, self).get_context_data(**kwargs)
        context_data['project_tab'] = ProjectTab.SETTINGS.value
        context_data['project_subtab'] = ProjectTab.SETTINGS_ACCESS.value
        return context_data


class ProjectSettingsSessionsView(ProjectPermissionsMixin, UpdateView):
    model = Project
    form_class = ProjectSettingsSessionsForm
    template_name = 'projects/project_settings_sessions.html'
    project_permission_required = ProjectPermissionType.MANAGE

    def get_context_data(self, **kwargs):
        context_data = super(ProjectSettingsSessionsView, self).get_context_data(**kwargs)
        context_data['parameters_presets'] = json.dumps(parameters_presets.parameters_presets)
        context_data['project_tab'] = ProjectTab.SETTINGS.value
        context_data['project_subtab'] = ProjectTab.SETTINGS_SESSIONS.value
        return context_data

    def get_initial(self):
        return self.form_class.initial(self.object)

    def get_success_url(self) -> str:
        return reverse('project_settings_sessions', args=(self.object.account.name, self.object.name))


class ProjectArchiveDownloadView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore  # doesn't match parent signature
        project = self.get_project(request.user, pk=pk)

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


class ProjectArchiveView(ArchivesDirMixin, ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW
    template_name = 'projects/project_archives.html'

    def get(self, request: HttpRequest, account_name: str, project_name: str, ) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, account_name, project_name)

        return render(request, self.template_name, self.get_archives_render_context(project))

    def get_archives_render_context(self, project: Project) -> dict:
        archives = self.list_archives(project)

        return self.get_render_context({
            'archives': archives,
            'form': ProjectArchiveForm(),
            'project_tab': ProjectTab.FILES.value,
            'project_subtab': ProjectTab.FILES_ARCHIVES.value
        })

    @staticmethod
    def get_archives_redirect(account_name: str, project_name: str) -> HttpResponse:
        return redirect('project_archives', account_name, project_name)

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

    def post(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        self.project_permission_required = ProjectPermissionType.EDIT
        project = self.get_project(request.user, account_name, project_name)

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

            return self.get_archives_redirect(account_name, project_name)

        form = ProjectArchiveForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, self.get_archives_render_context(project))

        puller = self.get_project_puller(request, account_name, project_name)

        archiver = ProjectArchiver(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project, request.user, puller)

        try:
            archiver.archive_project(form.cleaned_data['tag'])
        except Exception as e:
            messages.error(request, 'Archive failed: {}'.format(e))
        else:
            messages.success(request, 'Archive created successfully.')

        return self.get_archives_redirect(account_name, project_name)


class ProjectNamedArchiveDownloadView(ArchivesDirMixin, ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str,  # type: ignore
            name: str) -> FileResponse:
        project = self.get_project(request.user, account_name, project_name)

        archives_directory = self.get_archives_directory(project)
        archive_path = self.get_archive_path(archives_directory, name)

        if not path_is_in_directory(archive_path, archives_directory):
            raise PermissionDenied

        return FileResponse(open(to_utf8(archive_path), 'rb'), 'application/x-zip-compressed', as_attachment=True,
                            filename=name)


class ProjectExecutaView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, account_name, project_name)

        return render(request, 'projects/executa-test.html', {'project': project})


class ProjectSnapshotListView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, account_name, project_name)

        return render(request, 'projects/snapshot_list.html',
                      self.get_render_context({
                          'project': project,
                          'snapshots': project.snapshots.order_by('-version_number'),
                          'project_tab': ProjectTab.FILES.value,
                          'project_subtab': ProjectTab.FILES_SNAPSHOTS.value
                      }
                      ))
