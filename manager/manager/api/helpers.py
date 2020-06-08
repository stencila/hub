"""Helper functions for API views."""

import re
from typing import Dict, Optional, Union

from django.shortcuts import get_object_or_404


def filter_from_ident(
    value: str, prefix: Optional[str] = None, int_key="id", str_key="name"
) -> Dict[str, Union[str, int]]:
    """
    Get a filter dictionary from an identifier.

    If the identifier looks like an integer, then
    the filter has key `id`, otherwise `name`.
    """
    if re.match(r"\d+", value):
        key = int_key
        value = int(value)
    else:
        key = str_key
    if prefix is not None:
        key = prefix + "__" + key
    return {key: value}


def get_object_from_ident(cls, value: str):
    """Get an object from an indentifier."""
    return get_object_or_404(cls, **filter_from_ident(value))
