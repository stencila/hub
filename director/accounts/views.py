import typing

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView

from accounts.db_facade import AccountFetchResult, fetch_account
from accounts.forms import AccountSettingsForm, AccountCreateForm
from accounts.models import Account, AccountUserRole, AccountRole, AccountPermissionType

User = get_user_model()

USER_ROLE_ID_PREFIX = 'user_role_id_'


class AccountPermissionsMixin(LoginRequiredMixin):
    account_fetch_result: typing.Optional[AccountFetchResult] = None

    def perform_account_fetch(self, user: User, account_pk: int) -> None:
        self.account_fetch_result = fetch_account(user, account_pk)

    def get_render_context(self, context: dict) -> dict:
        context['account_permissions'] = self.account_permissions
        context['account_roles'] = self.account_roles
        return context

    def _test_account_fetch_result_set(self) -> None:
        if not self.account_fetch_result:
            raise ValueError("account_fetch_result not set")

    @property
    def account(self) -> Account:
        self._test_account_fetch_result_set()
        return self.account_fetch_result.account

    @property
    def account_permissions(self) -> typing.Set[AccountPermissionType]:
        self._test_account_fetch_result_set()
        return self.account_fetch_result.user_permissions

    @property
    def account_roles(self) -> typing.Set[AccountRole]:
        self._test_account_fetch_result_set()
        return self.account_fetch_result.user_roles

    def has_permission(self, permission: AccountPermissionType) -> bool:
        return self.has_any_permissions((permission,))

    def has_any_permissions(self, permissions: typing.Iterable[AccountPermissionType]) -> bool:
        for permission in permissions:
            if permission in self.account_permissions:
                return True

        return False


class AccountListView(LoginRequiredMixin, ListView):
    template_name = "accounts/account_list.html"

    def get_queryset(self) -> QuerySet:
        """
        Only list those accounts that the user is a member of
        """
        return AccountUserRole.objects.filter(user=self.request.user).select_related('account')


class AccountProfileView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.perform_account_fetch(request.user, pk)

        teams = self.account.teams.all()

        if self.has_any_permissions((AccountPermissionType.ADMINISTER, AccountPermissionType.MODIFY)):
            # Members get to see who is on account
            users = [user_role.user for user_role in self.account.user_roles.all()]
        else:
            # Non-members don't get to see who is on account
            users = []

        return render(request, 'accounts/account_profile.html', self.get_render_context({
            'account': self.account,
            'projects': self.account.projects.all,
            'users': users,
            'teams': teams
        }))


class AccountAccessView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.perform_account_fetch(request.user, pk)

        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        access_roles = AccountUserRole.objects.filter(account=self.account)
        all_roles = AccountRole.objects.all()

        return render(request, 'accounts/account_access.html', self.get_render_context({
            'account': self.account,
            'access_roles': access_roles,
            'all_roles': all_roles,
            'USER_ROLE_ID_PREFIX': USER_ROLE_ID_PREFIX
        }))

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.perform_account_fetch(request.user, pk)

        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        all_roles = AccountRole.objects.all()

        account = self.account

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


class AccountSettingsView(AccountPermissionsMixin, UpdateView):
    model = Account
    form_class = AccountSettingsForm
    template_name = 'accounts/account_settings.html'

    def get_success_url(self) -> str:
        return reverse("account_profile", kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        self.perform_account_fetch(self.request.user, self.object.pk)
        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied
        return self.get_render_context(super(AccountSettingsView, self).get_context_data(**kwargs))


class AccountCreateView(AccountPermissionsMixin, CreateView):
    model = Account
    form_class = AccountCreateForm
    template_name = 'accounts/account_create.html'

    def form_valid(self, form):
        """
        If the account creation form is valid them make the current user the
        account creator
        """
        self.object = form.save()
        admin_role = AccountRole.objects.get(name='Account admin')
        AccountUserRole.objects.create(role=admin_role, account=self.object, user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        return reverse("account_profile", kwargs={'pk': self.object.pk})
