import enum
import functools
import typing

from projects.source_models import MimeTypeFromPathMixin, Source


class DirectoryEntryType(enum.Enum):
    FILE = enum.auto()
    DIRECTORY = enum.auto()
    LINKED_SOURCE = enum.auto()

    def __lt__(self, other):
        if type(self) != type(other):
            raise TypeError("Can not compare DirectoryEntryType with non DirectoryEntryType")

        if self == other:
            return False

        if self == DirectoryEntryType.DIRECTORY:
            return True  # if it's a DIRECTORY it's before the other

        if self == DirectoryEntryType.LINKED_SOURCE:
            return other == DirectoryEntryType.FILE  # if it's a LINKED_SOURCE it's just before a FILE

        return False  # it must be a FILE so after others


@functools.total_ordering
class DirectoryListEntry(MimeTypeFromPathMixin):
    name: str
    path: str
    type: DirectoryEntryType
    source: Source

    def __init__(self, name: str, path: str, entry_type: DirectoryEntryType, source: Source) -> None:
        self.name = name
        self.path = path
        self.type = entry_type
        self.source = source

    def __lt__(self, other) -> bool:
        if type(self) != type(other):
            raise TypeError("Can not compare DirectoryListEntry with non DirectoryListEntry")

        if self.type == other.type:
            return self.name < other.name

        if self.type == DirectoryEntryType.DIRECTORY:
            return True

        return self.type < other.type

    @property
    def is_directory(self) -> bool:
        return self.type in (DirectoryEntryType.DIRECTORY, DirectoryEntryType.LINKED_SOURCE)


class PathEntry(typing.NamedTuple):
    name: str
    path: str
