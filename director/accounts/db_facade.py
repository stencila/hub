import typing

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from accounts.models import Account, AccountRole, AccountPermissionType, AccountUserRole, Team

User = get_user_model()


class AccountFetchResult(typing.NamedTuple):
    """
    Represents the result of an account fetch for a `User`, includes:
    -- user_roles: roles the current user has for the `Account`
    -- user_permissions: all permissions the current user has for the `Account`, i.e. combined permissions of all roles
    """
    account: Account
    user_roles: typing.Set[AccountRole]
    user_permissions: typing.Set[AccountPermissionType]


def fetch_account(user: AbstractUser, account_pk: int) -> AccountFetchResult:
    """
    Fetch an `Account` raising a 404 if the `Account` with `account_pk` does not exist. Returns an
    `AccountFetchResult`. If the `user` does not have access to the `Account` then `AccountFetchResult.user_roles` and
    `AccountFetchResult.user_permissions` will be empty sets.
    """
    account = get_object_or_404(Account, pk=account_pk)
    account_user_roles = AccountUserRole.objects.filter(account=account, user=user)

    user_roles: typing.Set[AccountUserRole] = set()
    user_permissions: typing.Set[AccountPermissionType] = set()

    for account_user_role in account_user_roles:
        if account_user_role.role in user_roles:
            continue

        user_roles.add(account_user_role.role)

        user_permissions |= account_user_role.role.permissions_types()

    return AccountFetchResult(account, user_roles, user_permissions)


def fetch_admin_account(user: AbstractUser, account_pk: int) -> Account:
    """
    Fetches an account, raising exceptions: 404 if account does not exist, or PermissionDenied if user does not have
    administrative permissions for the Account.
    """
    account = get_object_or_404(Account, pk=account_pk)

    admin_roles = AccountRole.roles_with_permission(AccountPermissionType.ADMINISTER)

    if AccountUserRole.objects.filter(user=user, account=account, role__in=admin_roles).count() == 0:
        raise PermissionDenied

    return account


def fetch_member_account(user: AbstractUser, account_pk: int) -> AccountFetchResult:
    """
    Fetches an account, raising exceptions: 404 if account does not exist, or PermissionDenied if user does not have
    any permissions for the account.
    """
    account = get_object_or_404(Account, pk=account_pk)

    admin_roles = AccountRole.roles_with_permission(AccountPermissionType.ADMINISTER)

    user_account_roles = AccountUserRole.objects.filter(user=user, account=account)

    if user_account_roles.count() == 0:
        raise PermissionDenied

    has_admin_role = False

    for user_account_role in user_account_roles:
        if user_account_role.role in admin_roles:
            has_admin_role = True
            break

    return AccountFetchResult(account, has_admin_role)  # type: ignore # mypy does not understand typed namedtuples


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


def fetch_accounts_for_user(user: AbstractUser) -> typing.Iterable[Account]:
    """
    Get an Iterable (map) of  `Account`s the `user` has access to (has any permissions).
    """
    return map(lambda aur: aur.account, AccountUserRole.objects.filter(user=user).select_related('account'))
