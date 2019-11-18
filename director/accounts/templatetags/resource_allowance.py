import typing

from django import template

from accounts.models import Account
import lib.resource_allowance

register = template.Library()


@register.filter
def resource_allowed(account: Account, resource_name: str) -> bool:
    if not isinstance(account, Account) or not resource_name:
        return False

    return lib.resource_allowance.account_resource_allowed(account,
                                                           lib.resource_allowance.QuotaName(resource_name))


@register.filter
def resource_limit_met(account: Account, resource_name: str) -> bool:
    if not isinstance(account, Account) or not resource_name:
        return False

    return lib.resource_allowance.resource_limit_met(account, lib.resource_allowance.QuotaName(resource_name))


@register.filter
def resource_limit(account: Account, resource_name: str) -> typing.Union[float, int]:
    if not isinstance(account, Account) or not resource_name:
        return False

    return lib.resource_allowance.account_resource_limit(account, lib.resource_allowance.QuotaName(resource_name))
