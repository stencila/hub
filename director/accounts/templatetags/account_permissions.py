import typing

from django import template

from accounts.models import AccountPermissionType

register = template.Library()


@register.filter
def permissions_contain(permissions: typing.Set[AccountPermissionType], permission_type_name: str) -> bool:
    return AccountPermissionType(permission_type_name) in permissions
