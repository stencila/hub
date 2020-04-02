import enum
import typing

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from lib.constants import DISALLOWED_ACCOUNT_SLUGS, DISALLOWED_PROJECT_SLUGS


class SlugType(enum.Enum):
    ACCOUNT = enum.auto()
    PROJECT = enum.auto()


def clean_slug(slug: typing.Optional[str], usage: SlugType) -> typing.Optional[str]:
    if not slug:
        return None

    slug = slug.lower()

    invalid = False

    if usage == SlugType.ACCOUNT:
        if slug in DISALLOWED_ACCOUNT_SLUGS:
            invalid = True
    else:
        if slug in DISALLOWED_PROJECT_SLUGS:
            invalid = True

    if invalid:
        raise ValidationError(
            'The name "{}" is reserved and can not be used.'.format(slug)
        )

    return slug


def logged_in_or_none(user: User) -> typing.Optional[User]:
    """Since `AnonymousUser`s can't be saved to the DB, return None if user is anonymous."""
    if user.is_anonymous:
        return None

    return user
