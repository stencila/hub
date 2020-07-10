from typing import Callable, Dict, NamedTuple

from django.core.cache import cache
from django.db.models import Sum

from accounts.models import Account, AccountTeam, AccountTier, AccountUser
from jobs.models import Job
from manager.api.exceptions import AccountQuotaExceeded
from projects.models.files import File
from projects.models.projects import Project


class AccountQuota(NamedTuple):
    """
    A quota for an account.

    name: Name of the quota
    calc: A function to calculate the current value for an account
    default: Default value
    message: Message if the quota is exceeded
    """

    name: str
    calc: Callable[[Account], float]
    message: str

    def limit(self, account: Account) -> float:
        """Get the limit for this quota for an account."""
        tier_key = "account-tier-{id}".format(id=account.tier_id)
        tier = cache.get(tier_key)
        if tier is None:
            tier = AccountTier.objects.get(id=account.tier_id)
            cache.set(tier_key, tier)

        if hasattr(tier, self.name):
            return getattr(tier, self.name)
        else:
            raise RuntimeError(
                "Misconfiguration! AccountTier model does not have a '{name}' field!".format(
                    name=self.name
                )
            )

    def usage(self, account: Account) -> Dict[str, float]:
        """Calculate the usage for this quota for an account."""
        amount = self.calc(account)
        limit = self.limit(account)
        return dict(amount=amount, limit=limit, percent=amount / limit * 100)

    def check(self, account: Account):
        """Check whether a quota has been exceed for an account."""
        usage = self.usage(account)
        if usage["amount"] >= usage["limit"]:
            raise AccountQuotaExceeded({self.name: self.message})


def bytes_to_gigabytes(value: float) -> float:
    """Convert bytes to gigabytes."""
    return value / 1073741824.0


class AccountQuotas:
    """List of account quotas."""

    ORGS_CREATED = AccountQuota(
        "orgs_created",
        lambda account: Account.objects.filter(creator=account.user).count(),
        "Maximum number of organizations you can create has been reached. "
        "Please contact us.",
    )

    ACCOUNT_USERS = AccountQuota(
        "account_users",
        lambda account: AccountUser.objects.filter(account=account).count(),
        "Maximum number of users for the account has been reached. "
        "Please upgrade the plan for this account.",
    )

    ACCOUNT_TEAMS = AccountQuota(
        "account_teams",
        lambda account: AccountTeam.objects.filter(account=account).count(),
        "Maximum number of teams for the account has been reached. "
        "Please upgrade the plan for this account.",
    )

    PROJECTS_PUBLIC = AccountQuota(
        "projects_public",
        lambda account: Project.objects.filter(account=account, public=True).count(),
        "Maximum number of public projects for the account has been reached. "
        "Please upgrade the plan for this account, or use a different account.",
    )

    PROJECTS_PRIVATE = AccountQuota(
        "projects_private",
        lambda account: Project.objects.filter(account=account, public=False).count(),
        "Maximum number of private projects for the account has been reached. "
        "Please upgrade the plan for this account, or use a different account.",
    )

    STORAGE_WORKING = AccountQuota(
        "storage_working",
        lambda account: bytes_to_gigabytes(
            File.objects.filter(
                project__account=account, snapshot__isnull=True
            ).aggregate(storage=Sum("size"))["storage"]
            or 0
        ),
        "Storage limit for project working directories has been reached."
        "Please upgrade the plan for the account.",
    )

    STORAGE_SNAPSHOTS = AccountQuota(
        "storage_snapshots",
        lambda account: bytes_to_gigabytes(
            File.objects.filter(
                project__account=account, snapshot__isnull=False
            ).aggregate(storage=Sum("size"))["storage"]
            or 0
        ),
        "Snapshot storage limit has been reached."
        "Please upgrade the plan for the account.",
    )

    JOB_RUNTIME_MONTH = AccountQuota(
        "job_runtime_month",
        lambda account: (
            Job.objects.filter(project__account=account).aggregate(
                runtime=Sum("runtime")
            )["runtime"]
            or 0
        )
        / 60000,
        "Job minutes has been exceeded." "Please upgrade the plan for the account.",
    )

    @staticmethod
    def usage(account: Account) -> Dict[str, Dict[str, float]]:
        """
        Get a dictionary of usage of each account quota.
        """
        return dict(
            [
                (quota.name, quota.usage(account))
                for quota in vars(AccountQuotas).values()
                if isinstance(quota, AccountQuota)
            ]
        )
