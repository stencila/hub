import typing

from django import template

register = template.Library()


@register.filter
def escape_single_quotes(string: typing.Any) -> str:
    # TODO: this is not really "accounts" specific so it could me moved to a "stub" application containing non-specific
    # template tags

    if not string:
        return ''

    if not isinstance(string, str):
        string = str(string)

    return string.replace("'", "\\'")
