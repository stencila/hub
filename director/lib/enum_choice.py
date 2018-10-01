import enum
import typing


class EnumChoice(enum.Enum):
    """Adds as_choices for use with Django choice field."""

    @classmethod
    def as_choices(cls) -> typing.List[typing.Tuple[str, str]]:
        """
        Converts Enum options to list of tuples in the form (name, value) for use in Django choice field.
        The return type signature assumes the values of the Enum are strings but this might not always be the case.
        """
        return [(e.name, e.value) for e in cls]
