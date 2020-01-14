import json
import typing
from operator import attrgetter

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.html import escape
from django.views import View

from accounts.db_facade import fetch_team_for_account
from accounts.forms import TeamForm
from accounts.models import Team, AccountPermissionType
from accounts.url_helpers import account_redirect
from accounts.views import AccountPermissionsMixin
from lib.resource_allowance import resource_limit_met, QuotaName, get_subscription_upgrade_text
from projects.permission_models import ProjectRole, ProjectAgentRole, AgentType
from projects.project_models import Project

User = get_user_model()

AGENT_ROLE_ID_PREFIX = 'agent_role_id_'


class TeamDetailView(AccountPermissionsMixin, View):
    def test_team_create_quota(self, request: HttpRequest, team_pk: typing.Optional[int]) \
            -> typing.Optional[HttpResponse]:
        if team_pk is None and resource_limit_met(self.account, QuotaName.MAX_TEAMS):
            upgrade_message = get_subscription_upgrade_text(self.has_permission(AccountPermissionType.ADMINISTER),
                                                            self.account)

            messages.error(request, 'This account has reached the maximum number of teams allowed by its current '
                                    'subscription. {}'.format(upgrade_message), extra_tags='safe')

            return account_redirect('account_team_list', account=self.account)

        return None

    def get(self, request: HttpRequest, account_pk: typing.Optional[int] = None,
            account_slug: typing.Optional[str] = None, team_pk: typing.Optional[int] = None) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk, account_slug)
        assert self.account_fetch_result is not None

        max_teams_redirect = self.test_team_create_quota(request, team_pk)
        if max_teams_redirect:
            return max_teams_redirect

        team = fetch_team_for_account(self.account_fetch_result.account, team_pk)

        form = TeamForm(instance=team)
        if not self.has_permission(AccountPermissionType.ADMINISTER):
            for field in form.fields.values():
                field.disabled = True

        return render(request, 'accounts/team_detail.html', self.get_render_context({
            'tab': 'teams',
            'team_tab': 'metadata',
            'team': team,
            'account': self.account,
            'form': form
        }))

    def post(self, request: HttpRequest, account_pk: typing.Optional[int] = None,
             account_slug: typing.Optional[str] = None, team_pk: typing.Optional[int] = None) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk, account_slug)

        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        max_teams_redirect = self.test_team_create_quota(request, team_pk)
        if max_teams_redirect:
            return max_teams_redirect

        team = fetch_team_for_account(self.account, team_pk)

        form = TeamForm(request.POST, instance=team)

        if form.is_valid():
            form.save()
            if team_pk is None:
                update_verb = "created"
            else:
                update_verb = "updated"

            messages.success(request, "Team <em>{}</em> was {} successfully".format(escape(team.name), update_verb),
                             extra_tags='safe')
            return account_redirect('account_team_list', account=self.account)

        return render(request, 'accounts/team_detail.html', self.get_render_context({
            'tab': 'teams',
            'team_tab': 'metadata',
            'team': team,
            'account': self.account,
            'form': form
        }))


class TeamListView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, account_pk: typing.Optional[int] = None,
            account_slug: typing.Optional[str] = None) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk, account_slug)

        if not self.account_permissions:
            raise PermissionDenied
        # Assume if they have any Roles for the Account they have access to this page

        return render(request, 'accounts/account_teams.html', self.get_render_context({
            'tab': 'teams',
            'account': self.account,
            'teams': self.account.teams.all
        }))


class TeamMembersView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, team_pk: int, account_pk: typing.Optional[int] = None,
            account_slug: typing.Optional[str] = None) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk, account_slug)
        team = fetch_team_for_account(self.account, team_pk)

        current_members = list(map(lambda u: u.username, team.members.all()))

        return render(request, 'accounts/team_members.html', self.get_render_context({
            'tab': 'teams',
            'team_tab': 'members',
            'tab': 'teams',
            'account': self.account,
            'team': team,
            'current_members': json.dumps(current_members)
        }))

    def post(self, request: HttpRequest, team_pk: int, account_pk: typing.Optional[int] = None,
             account_slug: typing.Optional[str] = None) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk, account_slug)

        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        team = fetch_team_for_account(self.account, team_pk)

        action = request.POST.get('action')

        if action in ('add_member', 'remove_member'):
            username = request.POST['name']

            if username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    messages.error(request, 'User "{}" does not exist.'.format(username))
                else:
                    if action == 'add_member':
                        if user not in team.members.all():
                            team.members.add(user)
                            messages.success(request, "{} was added to team {}.".format(user.username, team))
                    elif action == 'remove_member':
                        if user in team.members.all():
                            team.members.remove(user)
                            messages.success(request, "{} was removed from team {}.".format(user.username, team))

        return account_redirect('account_team_members', [team_pk], account=self.account)


class TeamProjectsView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, team_pk: int, account_pk: typing.Optional[int] = None,
            account_slug: typing.Optional[str] = None) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk, account_slug)
        team = fetch_team_for_account(self.account, team_pk)
        project_roles = ProjectRole.objects.all()
        all_projects = self.account.projects.all()
        existing_project_roles = ProjectAgentRole.objects.filter(project__in=all_projects, agent_id=team.pk,
                                                                 content_type=ContentType.objects.get_for_model(Team))
        assigned_projects = list(map(attrgetter('project'), existing_project_roles))

        unassigned_projects = filter(lambda p: p not in assigned_projects, all_projects)
        # this filtering can't be done by the ORM due to using GenericForeignKey
        # Shouldn't be dealing with millions of projects per account so should be OK

        return render(request, 'accounts/team_projects.html', self.get_render_context({
            'tab': 'teams',
            'team_tab': 'projects',
            'account': self.account,
            'team': team,
            'total_project_count': all_projects.count(),
            'existing_project_roles': existing_project_roles,
            'unassigned_projects': list(unassigned_projects),
            'project_roles': project_roles,
            'project_roles_map': json.dumps(
                {existing_project_role.pk: existing_project_role.role_id for existing_project_role in
                 existing_project_roles}),
            'AGENT_ROLE_ID_PREFIX': AGENT_ROLE_ID_PREFIX
        }))

    def post(self, request: HttpRequest, team_pk: int, account_pk: typing.Optional[int] = None,
             account_slug: typing.Optional[str] = None) -> HttpResponse:
        self.perform_account_fetch(request.user, account_pk, account_slug)

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
        elif request.POST.get('action') == 'set_role':
            role = role_lookup[int(request.POST['role_id'])]
            project_agent_role = ProjectAgentRole.objects.get(pk=request.POST['project_agent_role_id'])

            if project_agent_role.agent_type != AgentType.TEAM:
                return JsonResponse({'success': False, 'message': 'The role you trying to update is not for a team.'})

            if project_agent_role.team != team:
                return JsonResponse(
                    {'success': False, 'message': 'The role you trying to update is not for this team.'})

            project_agent_role.role = role
            project_agent_role.save()
            return JsonResponse({'success': True,
                                 'message': "Access to the project '{}' was updated for this team.".format(
                                     project_agent_role.project.get_name())})

        return account_redirect('account_team_projects', [team.pk], account=self.account)
