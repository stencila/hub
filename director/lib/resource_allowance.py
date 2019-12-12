import enum
import json
import typing
from pathlib import Path

from django.urls import reverse
from djstripe.models import Subscription

from accounts.models import Account, AccountSubscription, ProductExtension, Team
from lib import data_size
from projects.project_models import Project


def get_subscription_upgrade_text(is_account_admin: bool, account: Account):
    """
    Generate some text and link for the user to go to the account subscriptions page.

    Returns an empty string if the user is not an admin for the given account.
    """
    sub_link = '<a href="{}" target="_blank" rel="noopener">Account Subscriptions</a>'.format(
        reverse('account_subscriptions_plan_list', args=(account.id,)))

    if is_account_admin:
        message_start = 'Please visit the '
    else:
        message_start = 'An account administrator can visit the '

    return '{} {} page to upgrade or add a subscription.'.format(message_start, sub_link)


class QuotaName(enum.Enum):
    MAX_PRIVATE_PROJECTS = 'max_private_projects'
    MAX_PROJECTS = 'max_projects'
    MAX_TEAMS = 'max_teams'
    MAX_SESSION_DURATION = 'max_session_duration'  # in seconds
    MAX_CLIENTS_PER_SESSION = 'max_clients_per_session'
    SESSION_CPU_LIMIT = 'session_cpu_limit'
    SESSION_MEMORY_LIMIT = 'session_memory_limit'
    STORAGE_LIMIT = 'storage_limit'


QUOTA_DEFAULTS = {
    QuotaName.MAX_PROJECTS: 10,
    QuotaName.MAX_TEAMS: 0,
    QuotaName.MAX_SESSION_DURATION: 60 * 30,  # 30 mins
    QuotaName.MAX_CLIENTS_PER_SESSION: 2,
    QuotaName.SESSION_CPU_LIMIT: 10,
    QuotaName.SESSION_MEMORY_LIMIT: data_size.to_bytes(1, data_size.Units.GB),
    QuotaName.STORAGE_LIMIT: data_size.to_bytes(20, data_size.Units.MB)
}


class QuotaExceededException(Exception):
    pass


class StorageLimitExceededException(QuotaExceededException):
    pass


def active_subscriptions(account: Account) -> typing.List[Subscription]:
    return [subscription.subscription for subscription in account.subscriptions.all() if
            subscription.subscription.is_status_current()]


def account_resource_allowance(account: Account) -> dict:
    """Get all ResourceAllowances for all Subscriptions of an Account, then add up their limits."""
    totals: typing.Dict[str, typing.Any] = {}

    products = AccountSubscription.objects.filter(account=account,
                                                  subscription__status__in=('active', 'trialing')).values(
        'subscription__plan__product')

    product_extensions = ProductExtension.objects.filter(
        product__in=[product['subscription__plan__product'] for product in products])

    for pr in product_extensions:
        allowances: dict = json.loads(pr.allowances)

        for k, v in allowances.items():
            if k not in totals:
                totals[k] = v
            elif isinstance(v, bool):
                # Set the allowance to True if any allowances are True
                totals[k] = totals[k] or v
            elif isinstance(v, (int, float)):
                # add up numeric totals
                totals[k] = totals[k] + v
            else:
                # just set it
                totals[k] = v

    return totals


def account_resource_allowed(account: Account, name: QuotaName) -> bool:
    return account_resource_allowance(account).get(name.value, False)


def account_resource_limit(account: Account, name: QuotaName) -> typing.Union[int, float]:
    """Fetch a single resource limit."""
    return account_resource_limit_multiple(account, [name])[name]


def account_resource_limit_multiple(account: Account, names: typing.Iterable[QuotaName]) \
        -> typing.Dict[QuotaName, typing.Union[int, float]]:
    """Fetch multiple resource limits at once, in a single dictionary."""
    allowances = account_resource_allowance(account)

    computed_allowances = {}

    for name in names:
        default = QUOTA_DEFAULTS.get(name, 0)
        computed_allowances[name] = allowances.get(name.value, default)

    return computed_allowances


def current_resource_amount(account: Account, name: QuotaName) -> typing.Union[int, float]:
    """Get the current amount of the particular resource (given by `name`) currently in use by the `account`."""
    if name == QuotaName.MAX_PROJECTS:
        return Project.objects.filter(account=account).count()

    if name == QuotaName.MAX_PRIVATE_PROJECTS:
        return Project.objects.filter(account=account, public=False).count()

    if name == QuotaName.MAX_TEAMS:
        return Team.objects.filter(account=account).count()

    raise TypeError('Don\'t know how to fetch resource amount for {}'.format(name))


def resource_limit_met(account: Account, name: QuotaName) -> bool:
    resource_limit = account_resource_limit(account, name)
    if resource_limit == -1:
        return False

    if resource_limit == 0:
        return True

    current_value = current_resource_amount(account, name)

    return current_value >= resource_limit


def get_directory_size(path: str):
    """
    Get the size of the `path`, in bytes.

    Does not take into account the size of the directory entries or symlinks (which we shouldn't have) but is close
    enough for our quota purposes.
    """
    return sum(f.stat().st_size for f in Path(path).glob('**/*') if f.is_file())
