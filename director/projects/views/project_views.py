import json
import typing
from enum import Enum

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.html import escape
from django.views.generic import View, TemplateView, UpdateView, DetailView
from github import RateLimitExceededException

from accounts.db_facade import user_is_account_admin
from accounts.models import Team
from lib.resource_allowance import (
    QuotaName,
    resource_limit_met,
    get_subscription_upgrade_text,
    StorageLimitExceededException,
)
from lib.social_auth_token import user_github_token, user_supported_social_providers
from projects import parameters_presets
from projects.api.serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    ProjectDestroySerializer,
)
from projects.models import Project
from projects.permission_models import (
    ProjectPermissionType,
    ProjectRole,
    ProjectAgentRole,
    AgentType,
    get_roles_under_permission,
)
from projects.project_data import get_projects, FilterOption, FILTER_OPTIONS
from projects.project_forms import (
    ProjectSharingForm,
    ProjectSettingsSessionsForm,
)
from projects.source_models import (
    Source,
    FileSource,
    LinkedSourceAuthentication,
    DiskSource,
)
from projects.source_operations import (
    list_project_virtual_directory,
    path_entry_iterator,
    list_project_filesystem_directory,
    combine_virtual_and_real_entries,
)
from projects.views.mixins import ProjectPermissionsMixin
from projects.views.shared import DEFAULT_ENVIRON

User = get_user_model()


class ProjectTab(Enum):
    OVERVIEW = "overview"
    FILES = "files"
    FILES_SNAPSHOTS = "snapshots"
    JOBS = "jobs"
    SHARING = "sharing"
    SETTINGS = "settings"
    SETTINGS_SESSIONS = "sessions"


class ProjectNamedRedirect(View):
    def get(
        self, request: HttpRequest, pk: int, path: typing.Optional[str] = None
    ) -> HttpResponse:
        """Redirect old-style (id-based) URLs to new ones that use `name` as a slug."""
        project = get_object_or_404(Project, pk=pk)
        path = path or ""
        return redirect(
            "/{}/{}/{}".format(project.account.name, project.name, path), permanent=True
        )


class ProjectListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            filter_options: typing.Iterable[FilterOption] = []
        else:
            filter_options = FILTER_OPTIONS

        filter_option, projects, *_ = get_projects(
            request.user, request.GET.get("filter")
        )

        return render(
            request,
            "projects/project_list.html",
            {
                "object_list": projects,
                "filter": filter_option,
                "filter_options": filter_options,
            },
        )


class ProjectCreateView(LoginRequiredMixin, TemplateView):
    template_name = "projects/project_create.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["project_serializer"] = ProjectCreateSerializer(
            context=dict(request=self.request)
        )
        return context_data


class ProjectOverviewView(ProjectPermissionsMixin, DetailView):
    model = Project
    template_name = "projects/project_overview.html"
    project_permission_required = ProjectPermissionType.VIEW

    def get_context_data(self, **kwargs):
        context = super(ProjectOverviewView, self).get_context_data(**kwargs)
        environ = {"NIXSTER": "multi-mega"}.get(
            settings.EXECUTION_CLIENT, "stencila/core"
        )
        context["cloud_environ"] = environ
        context["project_tab"] = ProjectTab.OVERVIEW.value
        return context


class ProjectFilesView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(  # type: ignore
        self,
        request: HttpRequest,
        account_name: str,
        project_name: str,
        path: typing.Optional[str] = None,
    ) -> HttpResponse:
        self.get_project(request.user, account_name, project_name)

        authentication = LinkedSourceAuthentication(user_github_token(request.user))

        path = path or ""

        try:
            virtual_items = list_project_virtual_directory(
                self.project, path, authentication
            )
            on_disk_items = list_project_filesystem_directory(
                settings.STORAGE_DIR, self.project, path
            )

            directory_items = combine_virtual_and_real_entries(
                virtual_items, on_disk_items
            )
        except RateLimitExceededException:
            directory_items = []
            sa_c_url = reverse("socialaccount_connections")
            messages.error(
                request,
                "Could not list this directory as it contains Github sources and the anonymous "
                "rate limit has been exceeded.<br/>Please connect your Github account on the "
                '<a href="{}">Account Connections page</a> to remove this limit.'.format(
                    sa_c_url
                ),
                extra_tags="safe",
            )

        session_check_path = reverse("session_queue_v1", args=(self.project.token,))
        session_start_path = reverse(
            "session_start_v1", args=(self.project.token, DEFAULT_ENVIRON)
        )

        return render(
            request,
            "projects/project_files.html",
            self.get_render_context(
                {
                    "session_check_path": session_check_path,
                    "session_start_path": session_start_path,
                    "linked_sources": list(
                        self.project.sources.not_instance_of(FileSource)
                    ),
                    "current_directory": path,
                    "breadcrumbs": path_entry_iterator(path),
                    "item_names": json.dumps([item.name for item in directory_items]),
                    "items": directory_items,
                    "project_tab": ProjectTab.FILES.value,
                    "social_providers_supported": json.dumps(
                        user_supported_social_providers(request.user)
                    ),
                }
            ),
        )

    def post(  # type: ignore
        self,
        request: HttpRequest,
        account_name: str,
        project_name: str,
        path: typing.Optional[str] = None,
    ) -> HttpResponse:
        self.perform_project_fetch(request.user, account_name, project_name)
        if not self.has_permission(ProjectPermissionType.EDIT):
            raise PermissionDenied

        if request.POST.get("action") == "unlink_source":
            source_id = request.POST.get("source_id")

            if source_id:
                source = get_object_or_404(Source, project=self.project, pk=source_id)
            else:
                source = DiskSource()

            if isinstance(source, (FileSource, DiskSource)):
                raise TypeError("Can't unlink a File source")

            source_path = source.path

            source.delete()

            messages.success(
                request,
                "<em>{}</em> was unlinked.".format(escape(source_path)),
                extra_tags="safe",
            )

        return redirect(request.path)


class ProjectPullView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def post(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        puller = self.get_project_puller(request, account_name, project_name)
        try:
            puller.pull()
        except StorageLimitExceededException:
            is_account_admin = user_is_account_admin(
                self.request.user, self.project.account
            )
            subscription_upgrade_text = get_subscription_upgrade_text(
                is_account_admin, self.project.account
            )

            messages.error(
                request,
                "Could not pull the remote sources for this project, as it would exceed the storage limit "
                "for the account <em>{}</em>. {}".format(
                    escape(self.project.account), subscription_upgrade_text
                ),
                extra_tags="safe",
            )
            return JsonResponse({"success": False, "reload": True})
        return JsonResponse({"success": True})


class ProjectSharingView(ProjectPermissionsMixin, DetailView):
    model = Project
    form_class = ProjectSharingForm
    template_name = "projects/project_sharing.html"
    project_permission_required = ProjectPermissionType.MANAGE

    def get_context_data(self, **kwargs) -> dict:
        context_data = super().get_context_data(**kwargs)
        project_agent_roles = ProjectAgentRole.objects.filter(
            project=self.get_object()
        ).order_by("content_type")
        # ordering by content_type SHOULD end up with Users first because it being a built in Django model should be
        # created before Team

        context_data["project_agent_roles"] = project_agent_roles
        context_data["project_agent_role_map"] = json.dumps(
            {
                project_agent_role.pk: project_agent_role.role_id
                for project_agent_role in project_agent_roles
            }
        )

        context_data["all_roles"] = get_roles_under_permission(self.highest_permission)

        team_content_type = ContentType.objects.get_for_model(Team)

        context_data["user_content_type"] = ContentType.objects.get_for_model(User)
        context_data["team_content_type"] = team_content_type
        existing_teams = filter(
            lambda r: r.content_type == team_content_type, project_agent_roles
        )
        context_data["teams"] = Team.objects.filter(
            account=self.project.account
        ).exclude(pk__in=map(lambda r: r.agent_id, existing_teams))

        context_data["project_tab"] = ProjectTab.SHARING.value

        return context_data


class ProjectRoleUpdateView(ProjectPermissionsMixin, LoginRequiredMixin, View):
    project_permission_required = ProjectPermissionType.MANAGE

    def post(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        self.get_project(request.user, account_name, project_name)

        project_agent_role = None

        if request.POST.get("action") == "set_public":
            self.project.public = request.POST[
                "is_public"
            ] == "true" or resource_limit_met(
                self.project.account, QuotaName.MAX_PRIVATE_PROJECTS
            )
            self.project.save()
            return JsonResponse({"success": True})

        if request.POST.get("action") in ("set_role", "remove_role"):
            project_agent_role = get_object_or_404(
                ProjectAgentRole, pk=request.POST["project_agent_role_id"]
            )

        if (
            project_agent_role
            and project_agent_role.agent_type == AgentType.USER
            and project_agent_role.agent_id == request.user.pk
        ):
            raise PermissionDenied  # user can not change their own access

        if request.POST.get("action") == "remove_role":
            # mypy hint, only get here if project_agent_role is not None
            project_agent_role = typing.cast(ProjectAgentRole, project_agent_role)
            target_role = project_agent_role.role
        else:
            target_role = get_object_or_404(ProjectRole, pk=request.POST["role_id"])

        available_roles = get_roles_under_permission(self.highest_permission)

        if target_role not in available_roles:
            raise PermissionDenied  # user can not set/remove this role as it has permissions higher than what they have

        if request.POST.get("action") == "remove_role":
            # mypy hint, only get here if project_agent_role is not None
            project_agent_role = typing.cast(ProjectAgentRole, project_agent_role)
            agent_description = project_agent_role.agent_description
            project_agent_role.delete()
            messages.success(
                request,
                "Access to the project was removed from {}".format(agent_description),
            )
        elif request.POST.get("action") == "set_role":
            project_agent_role = get_object_or_404(
                ProjectAgentRole, pk=request.POST["project_agent_role_id"]
            )
            if project_agent_role.project != self.project:
                # user has permission on this Project but is trying to change the ProjectAgentRole on a different
                # Project
                raise PermissionDenied

            if project_agent_role.role != target_role:
                project_agent_role.role = target_role
                project_agent_role.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Access updated for {}".format(
                            project_agent_role.agent_description
                        ),
                    }
                )
        elif request.POST.get("action") in ("add_user_role", "add_team_role"):
            content_type_class = None
            agent_id = None

            if request.POST["action"] == "add_user_role":
                username = request.POST["name"]

                if not username:
                    raise ValueError("Blank username provided")

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    messages.error(
                        request, 'User "{}" does not exist.'.format(username)
                    )
                else:
                    if user == request.user:
                        messages.error(request, "You can not alter your own access.")
                    else:
                        agent_id = user.pk
                        content_type_class = User
            else:  # action == add_team_roles
                team_id = request.POST["team_id"]
                try:
                    team = Team.objects.get(pk=team_id)
                except Team.DoesNotExist:
                    messages.error(
                        request, "Team with ID {} does not exist.".format(team_id)
                    )
                else:
                    if team.account != self.project.account:
                        messages.error(
                            request,
                            "The selected Team does not belong to this account.",
                        )
                    else:
                        agent_id = team_id
                        content_type_class = Team

            if agent_id and content_type_class:
                project_agent_role, created = ProjectAgentRole.objects.update_or_create(
                    {"role": target_role},
                    project=self.project,
                    agent_id=agent_id,
                    content_type=ContentType.objects.get_for_model(content_type_class),
                )
                messages.success(
                    request,
                    "Account access added for {}.".format(
                        project_agent_role.agent_description
                    ),
                )

        return redirect("project_sharing", account_name, project_name)


class ProjectSettingsView(ProjectPermissionsMixin, DetailView):
    model = Project
    template_name = "projects/project_settings.html"
    project_permission_required = ProjectPermissionType.MANAGE

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["project_tab"] = ProjectTab.SETTINGS.value
        context_data["project_serializer"] = ProjectSerializer(self.object)
        context_data["project_destroy_serializer"] = ProjectDestroySerializer()
        return context_data


class ProjectSettingsSessionsView(ProjectPermissionsMixin, UpdateView):
    model = Project
    form_class = ProjectSettingsSessionsForm
    template_name = "projects/project_settings_sessions.html"
    project_permission_required = ProjectPermissionType.MANAGE

    def get_context_data(self, **kwargs):
        context_data = super(ProjectSettingsSessionsView, self).get_context_data(
            **kwargs
        )
        context_data["parameters_presets"] = json.dumps(
            parameters_presets.parameters_presets
        )
        context_data["project_tab"] = ProjectTab.SETTINGS.value
        context_data["project_subtab"] = ProjectTab.SETTINGS_SESSIONS.value
        return context_data

    def get_initial(self):
        return self.form_class.initial(self.object)

    def get_success_url(self) -> str:
        return reverse(
            "project_settings_sessions",
            args=(self.object.account.name, self.object.name),
        )


class ProjectExecutaView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, account_name, project_name)

        return render(request, "projects/executa-test.html", {"project": project})


class ProjectSnapshotListView(ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, account_name, project_name)

        return render(
            request,
            "projects/snapshot_list.html",
            self.get_render_context(
                {
                    "project": project,
                    "snapshots": project.snapshots.order_by("-version_number"),
                    "project_tab": ProjectTab.FILES_SNAPSHOTS.value,
                }
            ),
        )
