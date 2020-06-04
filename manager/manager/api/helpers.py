"""Helper functions for API views."""

import re
from typing import Dict, Optional, Union

from django.shortcuts import get_object_or_404


def get_filter_from_ident(
    value: str, prefix: Optional[str] = None
) -> Dict[str, Union[str, int]]:
    """
    Get a filter dictionary from an identifier.

    If the identifier looks like an integer, then
    the filter has key `id`, otherwise `name`.
    """
    if re.match(r"\d+", value):
        key = "id"
        value = int(value)
    else:
        key = "name"
    if prefix is not None:
        key = prefix + "__" + key
    return {key: value}


def get_object_from_ident(cls, value: str):
    """Get an object from an indentifier."""
    return get_object_or_404(cls, **get_filter_from_ident(value))
