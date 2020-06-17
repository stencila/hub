import enum
import re
from typing import List, Optional, Tuple

from django.db.models import Model, QuerySet
from django.template.defaultfilters import slugify


@enum.unique
class EnumChoice(enum.Enum):
    """
    An enumeration class with some additional convenience methods.

    Currently, the return type signatures assume the members of the enum
    are strings but this might not always be the case.
    """

    @classmethod
    def as_choices(cls) -> List[Tuple[str, str]]:
        """Convert members to a list of tuples for use in Django choice field."""
        return [(e.name, e.value) for e in cls]

    @classmethod
    def is_member(cls, value: str) -> bool:
        """Is the value a member of the enum."""
        return value in cls.__members__


def slug_strip(value: str, separator: str = "-") -> str:
    """
    Clean up a slug by removing slug separator characters.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ""
    if separator == "-" or not separator:
        re_sep = "-"
    else:
        re_sep = "(?:-|%s)" % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub("%s+" % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != "-":
            re_sep = re.escape(separator)
        value = re.sub(r"^%s+|%s+$" % (re_sep, re_sep), "", value)
    return value


def slug_start_dedigit(value: str):
    """
    Replace the first leading digit with the number as a word.

    This avoids having a slugs that looks the same as numeric ids in
    URLs (e.g. for accounts, projects). But, mainly for aesthetics,
    will also prevent any names with leading digits.
    """
    return re.sub(
        r"^\d",
        lambda match: {
            "0": "zero",
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
            "9": "nine",
        }[match.group(0)]
        + "-"
        if len(value) > 0
        else "",
        value,
    )


def unique_slugify(
    value: str,
    instance: Model = None,
    queryset: QuerySet = None,
    slug_field_name: str = "name",
    slug_len: Optional[int] = None,
    slug_separator: str = "-",
) -> str:
    """
    Calculate a unique slug of ``value``.

    ``queryset`` doesn't need to be provided if instance is  - it'll default
    to using the ``.all()`` queryset from the model's default manager.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    From https://djangosnippets.org/snippets/690/ with some modifications:
    - does not require an instance (can be used for input validation)
    - returns the slug instead of setting the field
    """
    if slug_len is None:
        if instance:
            slug_len = instance._meta.get_field(slug_field_name).max_length
        else:
            slug_len = 256

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    slug = re.sub("_", slug_separator, slug)
    if slug_len:
        slug = slug[:slug_len]
    slug = slug_strip(slug, slug_separator)
    slug = slug_start_dedigit(slug)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        if instance:
            queryset = instance.__class__._default_manager.all()
        else:
            raise RuntimeError("Must provide queryset or instance")
    if instance and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = "%s%s" % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[: slug_len - len(end)]
            slug = slug_strip(slug, slug_separator)
        slug = "%s%s" % (slug, end)
        next += 1

    return slug
