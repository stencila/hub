from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View, ListView, DetailView, UpdateView

from accounts.db_facade import fetch_admin_account
from accounts.models import Account, AccountUserRole, AccountRole

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


class AccountAccessView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        account = fetch_admin_account(request.user, pk)

        access_roles = AccountUserRole.objects.filter(account=account)
        all_roles = AccountRole.objects.all()

        return render(request, 'accounts/account_access.html', {
            'account': account,
            'access_roles': access_roles,
            'all_roles': all_roles,
            'USER_ROLE_ID_PREFIX': USER_ROLE_ID_PREFIX
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        account = fetch_admin_account(request.user, pk)

        all_roles = AccountRole.objects.all()

        role_lookup = {role.pk: role for role in all_roles}

        if request.POST.get('action') == 'add_access':
            username = request.POST['name']
            if username:
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
