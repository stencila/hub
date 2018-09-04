from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.base import View

from accounts.models import Account, AccountUserRole, AccountRole, AccountPermissionType

User = get_user_model()

USER_ROLE_ID_PREFIX = 'user_role_id_'


class AccountAccessView(LoginRequiredMixin, View):
    @staticmethod
    def fetch_account(request: HttpRequest, pk: int) -> Account:
        account = get_object_or_404(Account, pk=pk)

        admin_roles = AccountRole.roles_with_permission(AccountPermissionType.ADMINISTER)

        if AccountUserRole.objects.filter(user=request.user, account=account, role__in=admin_roles).count() == 0:
            raise PermissionDenied

        return account

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        account = self.fetch_account(request, pk)

        access_roles = AccountUserRole.objects.filter(account=account)
        all_roles = AccountRole.objects.all()

        return render(request, 'accounts/account_access.html', {
            'account': account,
            'access_roles': access_roles,
            'all_roles': all_roles,
            'USER_ROLE_ID_PREFIX': USER_ROLE_ID_PREFIX
        })

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        account = self.fetch_account(request, pk)

        all_roles = AccountRole.objects.all()

        role_lookup = {role.pk: role for role in all_roles}

        if request.POST.get('action') == 'add_access':
            username = request.POST['name']
            user = User.objects.get(username=username)

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
