from typing import Callable, NamedTuple

from accounts.models.account import Account, AccountTeam, AccountUser
from manager.api.exceptions import AccountQuotaExceeded
from projects.models import Project


class AccountQuota(NamedTuple):
    """
    A quota for an account.

    name: Name of the quota
    default: Default value
    message: Message if the quota is exceeded
    """

    name: str
    calc: Callable[[Account], float]
    default: float
    message: str

    def check(self, account: Account):
        """Check whether a quota has been exceed for an account."""
        # TODO: Check against the account plan for non-default values
        # TODO: Append a link to upgrade the plan for the account
        if self.calc(account) >= self.default:
            raise AccountQuotaExceeded({self.name: self.message})


class AccountQuotas:
    """List of account quotas."""

    ORGS = AccountQuota(
        "organizations",
        lambda account: Account.objects.filter(creator=account.user).count(),
        10,
        "Maximum number of organizations you can create has been reached. "
        "Please contact us.",
    )

    USERS = AccountQuota(
        "account_users",
        lambda account: AccountUser.objects.filter(account=account).count(),
        5,
        "Maximum number of users for the account has been reached. "
        "Please upgrade the plan for this account.",
    )

    TEAMS = AccountQuota(
        "account_teams",
        lambda account: AccountTeam.objects.filter(account=account).count(),
        5,
        "Maximum number of teams for the account has been reached. "
        "Please upgrade the plan for this account.",
    )

    PROJECTS_TOTAL = AccountQuota(
        "projects_total",
        lambda account: Project.objects.filter(account=account).count(),
        100,
        "Maximum number of projects for the account has been reached. "
        "Please upgrade the plan for this account, or use a different account.",
    )

    PROJECTS_PRIVATE = AccountQuota(
        "projects_private",
        lambda account: Project.objects.filter(account=account, public=False).count(),
        1,
        "Maximum number of private projects for the account has been reached. "
        "Please upgrade the plan for this account, or use a different account.",
    )
