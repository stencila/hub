import typing

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from accounts.db_facade import fetch_admin_account, fetch_team_for_account, fetch_member_account
from accounts.forms import TeamForm
from accounts.models import Account, AccountUserRole

User = get_user_model()


class TeamDetailView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, account_pk: int, team_pk: typing.Optional[int] = None) -> HttpResponse:
        account_result = fetch_member_account(request.user, account_pk)
        team = fetch_team_for_account(account_result.account, team_pk)

        form = TeamForm(instance=team)
        if not account_result.is_admin:
            for field in form.fields.values():
                field.disabled = True

        return render(request, "accounts/team_detail.html", {
            "is_admin": account_result.is_admin,
            "team": team,
            "account": account_result.account,
            "form": form
        })

    def post(self, request: HttpRequest, account_pk: int, team_pk: typing.Optional[int] = None) -> HttpResponse:
        account = fetch_admin_account(request.user, account_pk)
        # if account is retrieved then user must have admin access
        team = fetch_team_for_account(account, team_pk)

        form = TeamForm(request.POST, instance=team)

        if form.is_valid():
            form.save()
            if team_pk is None:
                update_verb = "created"
            else:
                update_verb = "updated"

            messages.success(request, "Team '{}' was {} successfully".format(team.name, update_verb))
            return redirect(reverse('account_team_list', args=(account.id,)))

        return render(request, "accounts/team_detail.html", {
            "team": team,
            "account": account,
            "form": form
        })


class TeamListView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, account_pk: int) -> HttpResponse:
        account = get_object_or_404(Account, pk=account_pk)
        if AccountUserRole.objects.filter(user=request.user, account=account).count() == 0:
            raise PermissionDenied
        # Assume if they have any Roles for the Account they have access

        return render(request, "accounts/account_teams.html", {
            "account": account,
            "teams": account.teams.all
        })


class TeamMembersView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, account_pk: int, team_pk: int) -> HttpResponse:
        account_result = fetch_member_account(request.user, account_pk)
        team = fetch_team_for_account(account_result.account, team_pk)

        return render(request, "accounts/team_members.html", {
            "is_admin": account_result.is_admin,
            "account": account_result.account,
            "team": team
        })

    def post(self, request: HttpRequest, account_pk: int, team_pk: int) -> HttpResponse:
        account = fetch_admin_account(request.user, account_pk)

        team = fetch_team_for_account(account, team_pk)

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
