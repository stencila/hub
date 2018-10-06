import functools
import typing

from projects.project_models import Project
from projects.source_models import Source


@functools.total_ordering
class SourcePath(typing.NamedTuple):
    source: Source
    name: str
    is_directory: bool

    def __lt__(self, other) -> bool:
        if type(self) != type(other):
            raise TypeError("Can not compare SourcePath with non SourcePath")

        if self.is_directory == other.is_directory:
            return self.name < other.name

        return self.is_directory  # directories are always < (before) non directories


class PathEntry(typing.NamedTuple):
    name: str
    path: str


def sources_in_directory(directory: typing.Optional[str], sources: typing.Iterable[Source]) \
        -> typing.Iterable[SourcePath]:
    """Yield a `SourcePath` for each `Source` passed in as `sources`, if the `Source` is inside the given directory."""
    seen_directories: typing.Set[str] = set()

    if directory:
        split_directory = directory.split('/')
        directory_depth = len(split_directory)
    else:
        split_directory = []
        directory_depth = 0

    for source in sources:
        if directory and not source.path.startswith(directory):
            continue

        split_path = source.path.split('/')

        if directory and split_directory != split_path[:directory_depth]:
            continue

        if split_path == split_directory:
            continue

        # since we are dealing with Unix paths only within containers, separator will always be /

        relative_path = split_path[directory_depth:]

        item_name = relative_path[0]

        item_is_directory = len(relative_path) > 1

        if item_is_directory:
            if item_name in seen_directories:
                continue
            seen_directories.add(item_name)

        yield SourcePath(source, item_name, item_is_directory)


def list_project_virtual_directory(project: Project, directory: typing.Optional[str]) -> typing.List[SourcePath]:
    """
    Generate a list of `SourcePath`s for all the `Source`s that belong to a `Project`, in the given `directory`.
    If `directory` is `None` then list the 'root' directory.
    """
    sources = project.sources.all()
    return sorted(list(sources_in_directory(directory, sources)))


def path_entry_iterator(path: typing.Optional[str]) -> typing.Iterable[PathEntry]:
    """
    Iterator to generate `PathEntry` objects, a tuple containing the current item name and the path to that item
    (including the item). The first entry is always /.

    For example, the path foo/bar/baz will yield:
    PathEntry('/', '')
    PathEntry('foo', 'foo')
    PathEntry('bar', 'foo/bar')
    PathEntry('baz', 'foo/bar/baz')
    """
    yield PathEntry('Files', '')

    if path:
        split_path = path.split('/')

        for i, name in enumerate(split_path):
            yield PathEntry(split_path[i], '/'.join(split_path[:i + 1]))
