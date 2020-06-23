import enum
from enum import unique


@unique
class ProjectPaths(enum.Enum):
    """
    Contains all the paths used in account urlpatterns.

    The purpose of this is to make it easier to keep the list of
    disallowed file paths within a project, up to date.
    """

    jobs = "jobs"
    sharing = "sharing"
    settings = "settings"
    sources = "sources"

    @classmethod
    def has(cls, value: str):
        """Check if this enum has a value."""
        return value in cls._value2member_map_  # type: ignore
