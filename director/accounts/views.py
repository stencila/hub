import typing

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View, ListView, DetailView, UpdateView

from accounts.forms import TeamForm
from accounts.models import Account, AccountUserRole, AccountRole, AccountPermissionType, Team

User = get_user_model()

USER_ROLE_ID_PREFIX = 'user_role_id_'


class AccountListView(LoginRequiredMixin, ListView):
    template_name = "accounts/account_list.html"

    def get_queryset(self) -> QuerySet:
        """
        Only list those accounts that the user is a member of
        """
        return AccountUserRole.objects.filter(user=self.request.user).select_related('account')


class AccountProfileView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'accounts/account_profile.html'


def fetch_account(user: User, account_pk: int) -> Account:
    """
    Fetches an account, raising exceptions: 404 if account does not exist, or PermissionDenied if user does not have
    administrative permissions for the Account.
    """
    account = get_object_or_404(Account, pk=account_pk)

    admin_roles = AccountRole.roles_with_permission(AccountPermissionType.ADMINISTER)

    if AccountUserRole.objects.filter(user=user, account=account, role__in=admin_roles).count() == 0:
        raise PermissionDenied

    return account


def fetch_team_for_account(account: Account, team_pk: typing.Optional[int]) -> Team:
    """
    Get Team with pk=team_pk. If team_pk is None a new Team is instantiated and returned (not saved to DB). The
    function checks if the Team belongs to the passed in Account and if not raises PermissionDenied. It is assumed
    that the current user already has administrative permissions for the Account and this has been checked.
    """
    if team_pk is not None:
        team = get_object_or_404(Team, pk=team_pk)
        if team.account != account:
            raise PermissionDenied
    else:
        team = Team()
        team.account = account

    return team


class AccountAccessView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        account = fetch_account(request.user, pk)

        access_roles = AccountUserRole.objects.filter(account=account)
        all_roles = AccountRole.objects.all()

        return render(request, 'accounts/account_access.html', {
            'account': account,
            'access_roles': access_roles,
            'all_roles': all_roles,
            'USER_ROLE_ID_PREFIX': USER_ROLE_ID_PREFIX
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        account = fetch_account(request.user, pk)

        all_roles = AccountRole.objects.all()

        role_lookup = {role.pk: role for role in all_roles}

        if request.POST.get('action') == 'add_access':
            username = request.POST['name']
            user = User.objects.get(username=username)

            if user == request.user:
                messages.error(request, "You can not alter your own access.")
            else:
                role = AccountRole.objects.get(pk=request.POST['role_id'])

                AccountUserRole.objects.update_or_create({
                    'role': role
                }, user=user, account=account)
                messages.success(request, "Account access updated.")
        elif request.POST.get('action') == 'delete_access':
            account_user_role = AccountUserRole.objects.get(pk=request.POST['user_role_id'])
            if account_user_role.account != account:
                raise PermissionDenied

            role_user = account_user_role.user

            if role_user == request.user:
                messages.error(request, "You can not remove account access from yourself.")
            else:
                account_user_role.delete()
                messages.success(request, "Access to the account for '{}' was removed.".format(role_user.username))
        else:
            for post_key, value in request.POST.items():
                if post_key.startswith(USER_ROLE_ID_PREFIX):
                    user_role_id = post_key[len(USER_ROLE_ID_PREFIX):]
                    account_user_role = AccountUserRole.objects.get(pk=user_role_id)

                    if account_user_role.user == request.user:
                        continue
                    if account_user_role.account != account:
                        raise PermissionDenied

                    new_role = role_lookup[int(value)]

                    if new_role != account_user_role.role:
                        account_user_role.role = new_role
                        account_user_role.save()
                        messages.success(request, "Role updated for user {}".format(account_user_role.user.username))

        return redirect(reverse('account_access', args=(pk,)))


class AccountTeamsView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'accounts/account_teams.html'


class AccountSettingsView(LoginRequiredMixin, UpdateView):
    model = Account
    fields = ['name']
    template_name = 'accounts/account_settings.html'


class TeamDetailView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, account_pk: int, team_pk: typing.Optional[int] = None) -> HttpResponse:
        account = fetch_account(request.user, account_pk)  # if account is retrieved then user must have admin access
        team = fetch_team_for_account(account, team_pk)

        form = TeamForm(instance=team)

        return render(request, "accounts/team_detail.html", {
            "form": form
        })

    def post(self, request: HttpRequest, account_pk: int, team_pk: typing.Optional[int] = None) -> HttpResponse:
        account = fetch_account(request.user, account_pk)  # if account is retrieved then user must have admin access
        team = fetch_team_for_account(account, team_pk)

        form = TeamForm(request.POST, instance=team)

        if form.is_valid():
            form.save()
            if team_pk is None:
                update_verb = "created"
            else:
                update_verb = "updated"

            messages.success(request, "Team '{}' was {} successfully".format(team.name, update_verb))
            return redirect(reverse('team_list', args=(account.id,)))

        return render(request, "accounts/team_detail.html", {
            "form": form
        })


class TeamListView(LoginRequiredMixin, View):
    pass
