from django import template

register = template.Library()


@register.filter
def escape_single_quotes(string: str) -> str:
    # TODO: this is not really "accounts" specific so it could me moved to a "stub" application containing non-specific
    # template tags
    return string.replace("'", "\\'")
