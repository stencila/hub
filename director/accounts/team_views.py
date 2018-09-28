import typing
from operator import attrgetter

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from accounts.db_facade import fetch_team_for_account
from accounts.forms import TeamForm
from accounts.models import Team, AccountPermissionType
from accounts.views import AccountPermissionsMixin
from projects.permission_models import ProjectRole, ProjectAgentRole
from projects.project_models import Project

User = get_user_model()

AGENT_ROLE_ID_PREFIX = 'agent_role_id_'


class TeamDetailView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, account_pk: int, team_pk: typing.Optional[int] = None) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk)
        team = fetch_team_for_account(self.account_fetch_result.account, team_pk)

        form = TeamForm(instance=team)
        if not self.has_permission(AccountPermissionType.ADMINISTER):
            for field in form.fields.values():
                field.disabled = True

        return render(request, "accounts/team_detail.html", self.get_render_context({
            "team": team,
            "account": self.account,
            "form": form
        }))

    def post(self, request: HttpRequest, account_pk: int, team_pk: typing.Optional[int] = None) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk)

        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        team = fetch_team_for_account(self.account, team_pk)

        form = TeamForm(request.POST, instance=team)

        if form.is_valid():
            form.save()
            if team_pk is None:
                update_verb = "created"
            else:
                update_verb = "updated"

            messages.success(request, "Team '{}' was {} successfully".format(team.name, update_verb))
            return redirect(reverse('account_team_list', args=(self.account.id,)))

        return render(request, "accounts/team_detail.html", self.get_render_context({
            "team": team,
            "account": self.account,
            "form": form
        }))


class TeamListView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, account_pk: int) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk)

        if not self.account_permissions:
            raise PermissionDenied
        # Assume if they have any Roles for the Account they have access to this page

        return render(request, "accounts/account_teams.html", self.get_render_context({
            "account": self.account,
            "teams": self.account.teams.all
        }))


class TeamMembersView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, account_pk: int, team_pk: int) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk)
        team = fetch_team_for_account(self.account, team_pk)

        return render(request, "accounts/team_members.html", self.get_render_context({
            "account": self.account,
            "team": team
        }))

    def post(self, request: HttpRequest, account_pk: int, team_pk: int) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk)

        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        team = fetch_team_for_account(self.account, team_pk)

        action = request.POST.get('action')

        if action in ('add_member', 'remove_member'):
            username = request.POST['name']

            if username:
                user = User.objects.get(username=username)

                if action == 'add_member':
                    if user not in team.members.all():
                        team.members.add(user)
                        messages.success(request, "{} was added to team {}.".format(user.username, team))
                elif action == 'remove_member':
                    if user in team.members.all():
                        team.members.remove(user)
                        messages.success(request, "{} was removed from team {}.".format(user.username, team))

        return redirect(reverse('account_team_members', args=(account_pk, team_pk)))


class TeamProjectsView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, account_pk: int, team_pk: int) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk)
        team = fetch_team_for_account(self.account, team_pk)
        project_roles = ProjectRole.objects.all()
        all_projects = self.account.projects.all()
        existing_project_roles = ProjectAgentRole.objects.filter(project__in=all_projects, agent_id=team.pk,
                                                                 content_type=ContentType.objects.get_for_model(Team))
        assigned_projects = list(map(attrgetter('project'), existing_project_roles))

        unassigned_projects = filter(lambda p: p not in assigned_projects, all_projects)
        # this filtering can't be done by the ORM due to using GenericForeignKey
        # Shouldn't be dealing with millions of projects per account so should be OK

        return render(request, "accounts/team_projects.html", self.get_render_context({
            "account": self.account,
            "team": team,
            "total_project_count": all_projects.count(),
            "existing_project_roles": existing_project_roles,
            "unassigned_projects": list(unassigned_projects),
            "project_roles": project_roles,
            "AGENT_ROLE_ID_PREFIX": AGENT_ROLE_ID_PREFIX
        }))

    def post(self, request: HttpRequest, account_pk: int, team_pk: int) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk)

        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        team = fetch_team_for_account(self.account, team_pk)

        all_roles = ProjectRole.objects.all()

        role_lookup = {role.pk: role for role in all_roles}

        if request.POST.get('action') == 'add_project':
            role = role_lookup[int(request.POST['role_id'])]
            project = Project.objects.get(pk=request.POST['project_id'])
            ProjectAgentRole.objects.update_or_create({
                'role': role
            }, agent_id=team.pk, content_type=ContentType.objects.get_for_model(Team), project=project)
            messages.success(request, "Project access to {} for {} was saved.".format(project.name, team.name))
        elif request.POST.get('action') == 'remove_project':
            project_agent_role = ProjectAgentRole.objects.get(pk=request.POST['agent_role_id'])
            project = project_agent_role.project
            project_agent_role.delete()
            messages.success(request, "Project access to {} for {} was removed.".format(project.name, team.name))
        else:
            for post_key, value in request.POST.items():
                if post_key.startswith(AGENT_ROLE_ID_PREFIX):
                    project_agent_role_id = post_key[len(AGENT_ROLE_ID_PREFIX):]
                    project_agent_role = ProjectAgentRole.objects.get(pk=project_agent_role_id)

                    if project_agent_role.team != team or project_agent_role.project.account != self.account:
                        raise PermissionDenied

                    new_role = role_lookup[int(value)]

                    if new_role != project_agent_role.role:
                        project_agent_role.role = new_role
                        project_agent_role.save()
                        messages.success(request, "Role updated for project {}".format(project_agent_role.project.name))

        return redirect(reverse("account_team_projects", args=(self.account.pk, team.pk)))
