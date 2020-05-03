import enum
import typing


class EnumChoice(enum.Enum):
    """
    An enumeration class with some additional convenience methods.

    Currently, the return type signatures assume the members of the enum
    are strings but this might not always be the case.
    """

    @classmethod
    def as_choices(cls) -> typing.List[typing.Tuple[str, str]]:
        """Convert members to a list of tuples for use in Django choice field."""
        return [(e.name, e.value) for e in cls]

    @classmethod
    def is_member(cls, value: str) -> bool:
        """Is the value a member of the enum."""
        return value in cls.__members__
