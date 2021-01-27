import enum
from enum import unique


@unique
class AccountPaths(enum.Enum):
    """
    Contains all the paths used in account urlpatterns.

    The purpose of this is to make it easier to keep the list of
    disallowed project names up to date.
    """

    billing = "billing"
    plan = "plan"
    profile = "profile"
    publishing = "publishing"
    static = "static"  # May be used when serving account subdomains
    teams = "teams"
    users = "users"

    @classmethod
    def has(cls, value: str):
        """Check if this enum has a value."""
        return value in cls._value2member_map_  # type: ignore
