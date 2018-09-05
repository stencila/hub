import typing

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from accounts.models import Account, AccountRole, AccountPermissionType, AccountUserRole, Team

User = get_user_model()


class AccountFetchResult(typing.NamedTuple):
    """
    Represents the result of an account fetch, includes the account for a flag for if the User has admin access to the
    account.
    """
    account: Account
    is_admin: bool


def fetch_admin_account(user: User, account_pk: int) -> Account:
    """
    Fetches an account, raising exceptions: 404 if account does not exist, or PermissionDenied if user does not have
    administrative permissions for the Account.
    """
    account = get_object_or_404(Account, pk=account_pk)

    admin_roles = AccountRole.roles_with_permission(AccountPermissionType.ADMINISTER)

    if AccountUserRole.objects.filter(user=user, account=account, role__in=admin_roles).count() == 0:
        raise PermissionDenied

    return account


def fetch_member_account(user: User, account_pk: int) -> AccountFetchResult:
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

    return AccountFetchResult(account, has_admin_role)


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
