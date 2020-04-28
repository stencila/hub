import json
import typing

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View, ListView, CreateView, UpdateView

from accounts.db_facade import AccountFetchResult, fetch_account
from accounts.forms import AccountSettingsForm, AccountCreateForm
from accounts.models import Account, AccountUserRole, AccountRole, AccountPermissionType

User = get_user_model()

USER_ROLE_ID_PREFIX = "user_role_id_"


class AccountPermissionsMixin(LoginRequiredMixin):
    account_fetch_result: typing.Optional[AccountFetchResult] = None
    required_account_permission: AccountPermissionType

    def perform_account_fetch(
        self,
        user: AbstractUser,
        account_name: typing.Optional[str] = None,
        pk: typing.Optional[int] = None,
    ) -> None:
        self.account_fetch_result = fetch_account(user, account_name, pk)

    def get_render_context(self, context: dict) -> dict:
        context["account_permissions"] = self.account_permissions
        context["account_roles"] = self.account_roles
        context["account"] = self.account
        context["is_account_admin"] = self.has_permission(
            AccountPermissionType.ADMINISTER
        )
        return context

    def _test_account_fetch_result_set(self) -> None:
        if not self.account_fetch_result:
            raise ValueError("account_fetch_result not set")

    # mypy is told to ignore type checking on these property returns as it doesn't understand that
    # `_test_account_fetch_result_set` checks for None

    @property
    def account(self) -> Account:
        self._test_account_fetch_result_set()
        return self.account_fetch_result.account  # type: ignore

    @property
    def account_permissions(self) -> typing.Set[AccountPermissionType]:
        self._test_account_fetch_result_set()
        return self.account_fetch_result.user_permissions  # type: ignore

    @property
    def account_roles(self) -> typing.Set[AccountRole]:
        self._test_account_fetch_result_set()
        return self.account_fetch_result.user_roles  # type: ignore

    def has_permission(self, permission: AccountPermissionType) -> bool:
        return self.has_any_permissions((permission,))

    def has_any_permissions(
        self, permissions: typing.Iterable[AccountPermissionType]
    ) -> bool:
        for permission in permissions:
            if permission in self.account_permissions:
                return True

        return False

    def is_permitted(
        self,
        user: AbstractUser,
        permission: AccountPermissionType,
        account_name: typing.Optional[str] = None,
        pk: typing.Optional[int] = None,
    ) -> bool:
        """Fetch an `Account` using its `pk` or `name`, then determine if `user` has `permission` for the `Account`."""
        self.perform_account_fetch(user, account_name, pk)
        return self.has_permission(permission)

    def request_permissions_guard(
        self,
        request: HttpRequest,
        account_name: typing.Optional[str] = None,
        pk: typing.Optional[int] = None,
        permission: typing.Optional[AccountPermissionType] = None,
    ) -> None:
        """
        Test that the current user has permissions, raising `PermissionDenied` if not.

        Will validate on the passed in `permission` or if this is not set then use `self.required_account_permission`.
        """
        permission = permission or self.required_account_permission

        if not self.is_permitted(request.user, permission, account_name, pk):
            raise PermissionDenied(
                "User must have {} permission to do this.".format(permission)
            )


class AccountListView(LoginRequiredMixin, ListView):
    template_name = "accounts/account_list.html"

    def get_queryset(self) -> QuerySet:
        """Only list those accounts that the user is a member of."""
        return AccountUserRole.objects.filter(user=self.request.user).select_related(
            "account"
        )


class AccountNameRedirectView(View):
    def get(
        self, request: HttpRequest, pk: int, path: typing.Optional[str] = None
    ) -> HttpResponse:
        """Redirect old-style (id-based) URLs to new ones that use `name` as a slug."""
        account = get_object_or_404(Account, pk=pk)
        path = path or ""
        return redirect("/{}/{}".format(account.name, path), permanent=True)


class AccountProfileView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, account_name: str) -> HttpResponse:
        self.perform_account_fetch(request.user, account_name)

        teams = self.account.teams.all()
        if self.has_any_permissions(
            (
                AccountPermissionType.ADMINISTER,
                AccountPermissionType.MODIFY,
                AccountPermissionType.VIEW,
            )
        ):
            # Members get to see who is on account
            users = [user_role.user for user_role in self.account.user_roles.all()]
        else:
            # Non-members don't get to see who is on account
            users = []
        return render(
            request,
            "accounts/account_profile.html",
            self.get_render_context(
                {
                    "tab": "profile",
                    "account": self.account,
                    "projects": self.account.projects.all,
                    "users": users,
                    "teams": teams,
                }
            ),
        )


class AccountAccessView(AccountPermissionsMixin, View):
    def get(self, request: HttpRequest, account_name: str) -> HttpResponse:
        self.perform_account_fetch(request.user, account_name)

        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        access_roles = AccountUserRole.objects.filter(account=self.account)
        all_roles = AccountRole.objects.all()

        access_roles_map = {
            access_role.pk: access_role.role.pk for access_role in access_roles
        }

        current_usernames = list(map(lambda ar: ar.user.username, access_roles))

        return render(
            request,
            "accounts/account_access.html",
            self.get_render_context(
                {
                    "tab": "members",
                    "account": self.account,
                    "access_roles": access_roles,
                    "access_roles_map": json.dumps(access_roles_map),
                    "all_roles": all_roles,
                    "USER_ROLE_ID_PREFIX": USER_ROLE_ID_PREFIX,
                    "current_usernames": json.dumps(current_usernames),
                }
            ),
        )

    def post(self, request: HttpRequest, account_name: str) -> HttpResponse:
        self.perform_account_fetch(request.user, account_name)

        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied

        all_roles = AccountRole.objects.all()

        account = self.account

        role_lookup = {role.pk: role for role in all_roles}

        if request.POST.get("action") == "set_role":
            account_user_role = AccountUserRole.objects.get(
                pk=request.POST["account_user_role_id"]
            )

            if account_user_role.user == request.user:
                raise ValueError("Can not set access to active user.")
            if account_user_role.account != account:
                raise PermissionDenied

            new_role = role_lookup[int(request.POST["role_id"])]

            if new_role != account_user_role.role:
                account_user_role.role = new_role
                account_user_role.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Access for {} updated.".format(
                        account_user_role.user.username
                    ),
                }
            )

        elif request.POST.get("action") == "add_access":
            username = request.POST["name"]
            if username:
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
                        role = AccountRole.objects.get(pk=request.POST["role_id"])

                        AccountUserRole.objects.update_or_create(
                            {"role": role}, user=user, account=account
                        )
                        messages.success(request, "Account access updated.")
        elif request.POST.get("action") == "delete_access":
            account_user_role = AccountUserRole.objects.get(
                pk=request.POST["user_role_id"]
            )
            if account_user_role.account != account:
                raise PermissionDenied

            role_user = account_user_role.user

            if role_user == request.user:
                messages.error(
                    request, "You can not remove account access from yourself."
                )
            else:
                account_user_role.delete()
                messages.success(
                    request,
                    "Access to the account for '{}' was removed.".format(
                        role_user.username
                    ),
                )
        else:
            for post_key, value in request.POST.items():
                if post_key.startswith(USER_ROLE_ID_PREFIX):
                    user_role_id = post_key[len(USER_ROLE_ID_PREFIX) :]
                    account_user_role = AccountUserRole.objects.get(pk=user_role_id)

                    if account_user_role.user == request.user:
                        continue
                    if account_user_role.account != account:
                        raise PermissionDenied

                    new_role = role_lookup[int(value)]

                    if new_role != account_user_role.role:
                        account_user_role.role = new_role
                        account_user_role.save()
                        messages.success(
                            request,
                            "Role updated for user {}".format(
                                account_user_role.user.username
                            ),
                        )

        return redirect("account_access", self.account.name)


class AccountSettingsView(AccountPermissionsMixin, UpdateView):
    model = Account
    form_class = AccountSettingsForm
    template_name = "accounts/account_settings.html"
    required_account_permission = AccountPermissionType.ADMINISTER
    slug_url_kwarg = "account_name"
    slug_field = "name"

    def get_success_url(self) -> str:
        return reverse("account_profile", args=(self.object.name,))

    def get_context_data(self, **kwargs):
        self.perform_account_fetch(self.request.user, self.object.name)
        if not self.has_permission(AccountPermissionType.ADMINISTER):
            raise PermissionDenied
        kwargs["tab"] = "settings"
        return self.get_render_context(
            super(AccountSettingsView, self).get_context_data(**kwargs)
        )


class AccountCreateView(AccountPermissionsMixin, CreateView):
    model = Account
    form_class = AccountCreateForm
    template_name = "accounts/account_create.html"
    slug_url_kwarg = "account_name"
    slug_field = "name"

    def form_valid(self, form):
        """If the account creation form is valid them make the current user the account creator."""
        self.object = form.save()
        admin_role = AccountRole.objects.get(name="Account admin")
        AccountUserRole.objects.create(
            role=admin_role, account=self.object, user=self.request.user
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        return reverse("account_profile", args=(self.object.name,))
