import os
import typing

from github import GithubException

from lib.github_facade import GitHubFacade
from projects.project_models import Project
from projects.source_item_models import PathEntry, DirectoryListEntry, DirectoryEntryType

from projects.source_models import Source, FileSource, GithubSource


def normalise_path(path: str, append_slash: bool = False) -> str:
    if path == '.' or path == '':
        return ''

    return path if (not append_slash or path.endswith('/')) else (path + '/')


def path_is_in_directory(path: str, directory: str) -> bool:
    path = normalise_path(path)
    directory = normalise_path(directory, True)

    return path[:len(directory)] == directory


def strip_directory(path: str, directory: str) -> str:
    path = normalise_path(path)
    directory = normalise_path(directory, True)

    if path_is_in_directory(path, directory):
        return path[len(directory):]

    raise ValueError("Path {} is not in directory {}".format(path, directory))


def determine_entry_type(source: Source, relative_path: str) -> DirectoryEntryType:
    if isinstance(source, FileSource):
        return DirectoryEntryType.DIRECTORY if '/' in relative_path else DirectoryEntryType.FILE

    return DirectoryEntryType.LINKED_SOURCE


def list_linked_source_directory(source: Source, path_in_source: str, facade: typing.Optional[GitHubFacade] = None) \
        -> typing.Iterable[DirectoryListEntry]:
    if isinstance(source, GithubSource):
        if facade is None:
            raise TypeError("Can't list GitHub without a GitHubFacade passed in.")

        full_repository_path = os.path.join(source.subpath, path_in_source)
        for name, is_directory in facade.list_directory(full_repository_path):
            entry_type = DirectoryEntryType.DIRECTORY if is_directory else DirectoryEntryType.FILE
            yield DirectoryListEntry(name, os.path.join(source.path, path_in_source, name), entry_type, source)
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
        name = os.path.basename(relative_path)
    else:
        name = relative_path.split('/')[0]
    full_path = os.path.join(directory, name)
    return DirectoryListEntry(name, full_path, entry_type, source)


def sources_in_directory(directory: typing.Optional[str], sources: typing.Iterable[Source],
                         auth_tokens: typing.Optional[dict] = None) \
        -> typing.Iterable[DirectoryListEntry]:
    """Yield a `DirectoryListEntry` for each `Source` in `sources` if the `Source` is inside the `directory`."""
    directory = directory or ''
    auth_tokens = auth_tokens or {}
    seen_directories: typing.Set[str] = set()

    for source in sources:
        if isinstance(source, GithubSource):
            github_token = auth_tokens.get(GithubSource.provider_name)
            facade = GitHubFacade(source.repo, github_token)
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
                                   auth_tokens: typing.Optional[dict]) -> typing.List[DirectoryListEntry]:
    """
    Generate a list of `SourceItem`s for all the `Source`s that belong to a `Project`, in the given `directory`.

    If `directory` is `None` then list the 'root' directory.
    """
    sources = project.sources.all()
    return sorted(list(sources_in_directory(directory, sources, auth_tokens)))


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
