import datetime
import functools
import os
import typing
from operator import attrgetter
from os import DirEntry

from github import GithubException

from lib.github_facade import GitHubFacade
from projects.project_models import Project
from projects.source_item_models import PathEntry, DirectoryListEntry, DirectoryEntryType

from projects.source_models import Source, FileSource, GithubSource, LinkedSourceAuthentication, DiskSource

PathType = typing.Union[str, bytes]


def to_utf8(s: PathType) -> bytes:
    """If a `str` is passed in, return its utf8 encoding, ff `bytes`, assume it is already utf8 and just return it."""
    return s.encode('utf8') if isinstance(s, str) else s


def utf8_path_join(*args: PathType) -> str:
    """Encode `str` typed args into `bytes` using utf8 then passes all to `os.path.join`."""
    return os.path.join(*list(map(to_utf8, args))).decode('utf8')


def utf8_normpath(path: PathType) -> str:
    return os.path.normpath(to_utf8(path)).decode('utf8')


def utf8_isdir(path: PathType) -> bool:
    return os.path.isdir(to_utf8(path))


def utf8_basename(path: PathType) -> str:
    return os.path.basename(to_utf8(path)).decode('utf8')


def utf8_dirname(path: PathType) -> str:
    return os.path.dirname(to_utf8(path)).decode('utf8')


def utf8_realpath(path: PathType) -> str:
    return os.path.realpath(to_utf8(path)).decode('utf8')


def utf8_path_exists(path: PathType) -> bool:
    return os.path.exists(to_utf8(path))


def utf8_unlink(path: PathType) -> None:
    os.unlink(to_utf8(path))


def utf8_makedirs(path: PathType, *args, **kwargs) -> None:
    os.makedirs(to_utf8(path), *args, **kwargs)


def utf8_rename(src: PathType, dest: PathType):
    os.rename(to_utf8(src), to_utf8(dest))


def generate_project_storage_directory(project_storage_root: str, project: Project) -> str:
    return utf8_path_join(project_storage_root, 'projects', '{}'.format(project.id))


def generate_project_archive_directory(project_storage_root: str, project: Project) -> str:
    return utf8_path_join(project_storage_root, 'archives', '{}'.format(project.id))


def utf8_scandir(path: PathType) -> typing.Iterable[DirEntry]:
    yield from os.scandir(to_utf8(path))


def normalise_path(path: str, append_slash: bool = False) -> str:
    if path == '.' or path == '':
        return ''

    append_slash = append_slash or path.endswith('/')

    return utf8_normpath(path) + ('/' if append_slash else '')


def path_is_in_directory(path: str, directory: str, allow_matching: bool = False) -> bool:
    path = normalise_path(path)
    directory = normalise_path(directory, True)

    if path.startswith(directory):
        return True

    if not allow_matching:
        return False

    if not path.endswith('/'):
        path += '/'

    return path == directory


def strip_directory(path: str, directory: str) -> str:
    path = normalise_path(path)
    directory = normalise_path(directory, True)

    if path_is_in_directory(path, directory):
        return path[len(directory):]

    raise ValueError("Path {} is not in directory {}".format(path, directory))


def relative_path_join(directory: str, relative_path: str) -> str:
    """
    Join `relative_path` on to `directory`.

    Then ensure that the generated path is inside the `director`y (i.e. relative_path does not contain path traversal
    components).
    """
    full_path = utf8_realpath(utf8_path_join(directory, relative_path))

    if path_is_in_directory(full_path, directory):
        return full_path

    raise ValueError("Path {} is not in directory {}".format(full_path, directory))


def determine_entry_type(source: Source, relative_path: str) -> DirectoryEntryType:
    if isinstance(source, FileSource):
        return DirectoryEntryType.DIRECTORY if '/' in relative_path else DirectoryEntryType.FILE

    return DirectoryEntryType.LINKED_SOURCE


def list_linked_source_directory(source: Source, path_in_source: str, facade: typing.Optional[GitHubFacade] = None) \
        -> typing.Iterable[DirectoryListEntry]:
    if isinstance(source, GithubSource):
        if facade is None:
            raise TypeError("Can't list GitHub without a GitHubFacade passed in.")

        full_repository_path = utf8_path_join(source.subpath, path_in_source)
        for name, is_directory, modification_date in facade.list_directory(full_repository_path):
            entry_type = DirectoryEntryType.DIRECTORY if is_directory else DirectoryEntryType.FILE
            yield DirectoryListEntry(name, utf8_path_join(source.path, path_in_source, name), entry_type, source,
                                     modification_date)
    else:
        raise TypeError("Don't know how to list directory for source type {}".format(type(source)))


class IncorrectDirectoryException(Exception):
    """Raised if attempting to list a directory in a source that is not the current directory."""


def iterate_github_source(directory: str, source: GithubSource, facade: GitHubFacade):
    if normalise_path(source.path, True) == normalise_path(directory, True):
        directory = ''
    elif path_is_in_directory(directory, source.path):
        directory = strip_directory(directory, source.path)
    else:
        raise IncorrectDirectoryException

    try:
        yield from list_linked_source_directory(source, directory, facade)
    except GithubException as e:
        if e.status == 404:
            return DirectoryListEntry(directory.split('/')[0], directory, DirectoryEntryType.DIRECTORY, source)
        else:
            raise


def make_directory_entry(directory: str, source: Source):
    relative_path = strip_directory(source.path, directory)
    entry_type = determine_entry_type(source, relative_path)
    if entry_type == DirectoryEntryType.FILE:
        name = utf8_basename(relative_path)
    else:
        name = relative_path.split('/')[0]
    full_path = utf8_path_join(directory, name)
    return DirectoryListEntry(name, full_path, entry_type, source)


def sources_in_directory(directory: typing.Optional[str], sources: typing.Iterable[Source],
                         authentication: LinkedSourceAuthentication) -> typing.Iterable[DirectoryListEntry]:
    """Yield a `DirectoryListEntry` for each `Source` in `sources` if the `Source` is inside the `directory`."""
    directory = directory or ''
    seen_directories: typing.Set[str] = set()

    for source in sources:
        if isinstance(source, GithubSource):
            facade = GitHubFacade(source.repo, authentication.github_token)
            try:
                for entry in iterate_github_source(directory, source, facade):
                    if entry.type == DirectoryEntryType.DIRECTORY or entry.type == DirectoryEntryType.LINKED_SOURCE:
                        if entry.name in seen_directories:
                            continue
                        seen_directories.add(entry.name)
                    yield entry
                continue
            except IncorrectDirectoryException:
                pass

        if path_is_in_directory(source.path, directory):
            entry = make_directory_entry(directory, source)

            if entry.type == DirectoryEntryType.DIRECTORY or entry.type == DirectoryEntryType.LINKED_SOURCE:
                if entry.name in seen_directories:
                    continue
                seen_directories.add(entry.name)
            yield entry


def list_project_virtual_directory(project: Project, directory: typing.Optional[str],
                                   authentication: LinkedSourceAuthentication,
                                   only_file_sources: bool = False) -> typing.List[DirectoryListEntry]:
    """
    Generate a list of `SourceItem`s for all the `Source`s that belong to a `Project`, in the given `directory`.

    If `directory` is `None` then list the 'root' directory.
    """
    if only_file_sources:
        sources = project.sources.instance_of(FileSource)
    else:
        sources = project.sources.not_instance_of(FileSource)

    return sorted(list(sources_in_directory(directory, sources, authentication)))


def recursive_directory_list(project: Project, directory: typing.Optional[str],
                             authentication: LinkedSourceAuthentication) -> typing.Iterable[DirectoryListEntry]:
    for entry in list_project_virtual_directory(project, directory, authentication):
        path = utf8_path_join(directory or '', entry.name)
        if entry.is_directory:
            yield from recursive_directory_list(project, path, authentication)
        yield entry


def os_dir_entry_to_directory_list_entry(virtual_path: str, dir_entry: os.DirEntry) -> DirectoryListEntry:
    """Convert an `os.DirEntry` instance to a `DirectoryListEntry`."""
    s: os.stat_result = dir_entry.stat()

    return DirectoryListEntry(dir_entry.name.decode('utf8'), utf8_path_join(virtual_path, dir_entry.name),
                              DirectoryEntryType.DIRECTORY if dir_entry.is_dir() else DirectoryEntryType.FILE,
                              DiskSource(), datetime.datetime.fromtimestamp(s.st_mtime))


def list_project_filesystem_directory(project_storage_root: str, project: Project,
                                      relative_directory: typing.Optional[str]) -> typing.List[DirectoryListEntry]:
    relative_directory = relative_directory or ''
    directory_to_list = get_filesystem_project_path(project_storage_root, project, relative_directory)

    if not utf8_isdir(directory_to_list):
        return []

    return sorted(list(map(functools.partial(os_dir_entry_to_directory_list_entry, relative_directory),
                           utf8_scandir(directory_to_list))))


def get_filesystem_project_path(project_storage_root: str, project: Project, relative_path: str) -> str:
    """
    Get the path of a file relative to the `Project`'s storage directory.

    If path traversal is attempted (e.g. relative path contains '/../') then an OSError is raised.
    """
    project_storage_directory = utf8_realpath(generate_project_storage_directory(project_storage_root, project))
    project_path = utf8_realpath(utf8_path_join(project_storage_directory, relative_path))
    if not path_is_in_directory(project_path, project_storage_directory, True):
        raise OSError("Attempting to access path outside of project root.")
    return project_path


def combine_virtual_and_real_entries(virtual_files: typing.List[DirectoryListEntry],
                                     real_files: typing.List[DirectoryListEntry]) -> typing.List[DirectoryListEntry]:
    """
    Combine a list of virtual on real files with virtual files taking precedence over real.

    A real file should only be show in the list of files if it is not already represented by a virtual file (`Source`).

    The reason for this is that after a pull (e.g. from Github) the files will exist on disk but we won't know where
    they come from unless we can relate back to the `Source`.
    """
    name_getter = attrgetter('name')
    virtual_names = list(map(name_getter, virtual_files))

    return sorted(virtual_files + list(filter(lambda e: name_getter(e) not in virtual_names, real_files)))


def path_entry_iterator(path: typing.Optional[str] = '') -> typing.Iterable[PathEntry]:
    """
    Iterate each component of the `path` to generate `PathEntry` objects.

    Each PathEntry is a tuple containing the current item name and the path to that item (including the item as the
    last component). The first entry returned (yielded) is always /.

    For example, the path foo/bar/baz will yield:
    PathEntry('/', '')
    PathEntry('foo', 'foo')
    PathEntry('bar', 'foo/bar')
    PathEntry('baz', 'foo/bar/baz')
    """
    path = path or ''
    yield PathEntry('Files', '')

    if path:
        split_path = list(filter(lambda component: component != '.', path.split('/')))

        for i, name in enumerate(split_path):
            full_path = '/'.join(split_path[:i + 1])
            yield PathEntry(split_path[i], full_path)
