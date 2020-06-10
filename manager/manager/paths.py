import enum
from enum import unique


@unique
class Paths(enum.Enum):
    """
    Contains all the root paths used in the base urlpatterns.

    The purpose of this is to make it easier to keep the list of
    disallowed account names up to date.
    """

    api = "api"
    favicon = "favicon.ico"
    me = "me"
    orgs = "orgs"
    projects = "projects"
    users = "users"

    @classmethod
    def has(cls, value: str):
        """Check if this enum has a value."""
        return value in cls._value2member_map_
