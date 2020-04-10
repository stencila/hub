import datetime
import functools
import os
import typing
from operator import attrgetter

from github import GithubException

from lib.github_facade import GitHubFacade
from lib.path_operations import (
    utf8_path_join,
    utf8_isdir,
    utf8_basename,
    utf8_realpath,
    utf8_scandir,
    normalise_path,
    path_is_in_directory,
    utf8_dirname,
)
from projects.project_models import Project, Snapshot
from projects.source_item_models import (
    PathEntry,
    DirectoryListEntry,
    DirectoryEntryType,
)

from projects.source_models import (
    Source,
    FileSource,
    GithubSource,
    LinkedSourceAuthentication,
    DiskSource,
    GoogleDocsSource,
    UrlSource,
)


def generate_project_storage_directory(
    project_storage_root: str, project: Project
) -> str:
    return utf8_path_join(project_storage_root, "projects", "{}".format(project.id))


def generate_project_publish_directory(
    project_storage_root: str, project: Project
) -> str:
    """
    Generate the path to a directory that stores a published item.

    When changing the format here, please update the version in the path. After this path is generated it is stored on a
    PublishedItem in full, so we don't need to call this function again to generate a path, and don't need to worry
    about changing the format.
    The current format is STORAGE_ROOT/published/v2/<account_id // 1000>/<account_id>/<project_id>.
    """
    return utf8_path_join(
        project_storage_root,
        "published",
        "v2",
        "{}".format(project.account_id // 1000),
        "{}".format(project.account_id),
        "{}".format(project.id),
    )


def generate_snapshot_publish_directory(
    project_storage_root: str, snapshot: Snapshot
) -> str:
    """
    Generate the path to a a directory that stores a published item for a snapshot.

    This will be inside the project published directory, in a snapshots subfolder.
    The current format is: <PROJECT_PUBLISHED_DIR>/snapshots/<snapshot_version>
    """
    return utf8_path_join(
        generate_project_publish_directory(project_storage_root, snapshot.project),
        "snapshots",
        "{}".format(snapshot.version_number),
    )


def generate_snapshot_directory(project_storage_root: str, snapshot: Snapshot) -> str:
    """
    Generate the directory that stores the files for a Snapshot.

    After the path is generated it is stored on a Snapshot instance, so it's safe to change the return format, as it's
    only used once at generation time.

    The current format is STORAGE_ROOT/snapshots/<account_id // 1000>/<account_id>/<project_id>.
    """
    return utf8_path_join(
        project_storage_root,
        "snapshots",
        "{}".format(snapshot.project.account_id // 1000),
        "{}".format(snapshot.project.account_id),
        "{}".format(snapshot.project.id),
        "{}".format(snapshot.version_number),
    )


def strip_directory(path: str, directory: str) -> str:
    path = normalise_path(path)
    directory = normalise_path(directory, True)

    if path_is_in_directory(path, directory):
        return path[len(directory) :]

    raise ValueError("Path {} is not in directory {}".format(path, directory))


def determine_entry_type(source: Source, relative_path: str) -> DirectoryEntryType:
    if isinstance(source, FileSource):
        return (
            DirectoryEntryType.DIRECTORY
            if "/" in relative_path
            else DirectoryEntryType.FILE
        )

    if isinstance(source, (GoogleDocsSource, UrlSource)):
        return DirectoryEntryType.FILE

    return DirectoryEntryType.LINKED_SOURCE


def list_linked_source_directory(
    source: Source, path_in_source: str, facade: typing.Optional[GitHubFacade] = None
) -> typing.Iterable[DirectoryListEntry]:
    if isinstance(source, GithubSource):
        if facade is None:
            raise TypeError("Can't list GitHub without a GitHubFacade passed in.")

        full_repository_path = utf8_path_join(source.subpath, path_in_source)
        for name, is_directory, modification_date in facade.list_directory(
            full_repository_path
        ):
            entry_type = (
                DirectoryEntryType.DIRECTORY
                if is_directory
                else DirectoryEntryType.FILE
            )
            yield DirectoryListEntry(
                name,
                utf8_path_join(source.path, path_in_source, name),
                entry_type,
                source,
                modification_date,
            )
    else:
        raise TypeError(
            "Don't know how to list directory for source type {}".format(type(source))
        )


class IncorrectDirectoryException(Exception):
    """Raised if attempting to list a directory in a source that is not the current directory."""


def iterate_github_source(directory: str, source: GithubSource, facade: GitHubFacade):
    if normalise_path(source.path, True) == normalise_path(directory, True):
        directory = ""
    elif path_is_in_directory(directory, source.path):
        directory = strip_directory(directory, source.path)
    else:
        raise IncorrectDirectoryException

    try:
        yield from list_linked_source_directory(source, directory, facade)
    except GithubException as e:
        if e.status == 404:
            return DirectoryListEntry(
                directory.split("/")[0], directory, DirectoryEntryType.DIRECTORY, source
            )
        else:
            raise


def make_directory_entry(directory: str, source: Source):
    relative_path = strip_directory(source.path, directory)
    entry_type = determine_entry_type(source, relative_path)
    if entry_type == DirectoryEntryType.FILE:
        name = utf8_basename(relative_path)
    else:
        name = relative_path.split("/")[0]
    full_path = utf8_path_join(directory, name)
    return DirectoryListEntry(name, full_path, entry_type, source)


def sources_in_directory(
    directory: typing.Optional[str],
    sources: typing.Iterable[Source],
    authentication: LinkedSourceAuthentication,
) -> typing.Iterable[DirectoryListEntry]:
    """Yield a `DirectoryListEntry` for each `Source` in `sources` if the `Source` is inside the `directory`."""
    directory = directory or ""
    seen_directories: typing.Set[str] = set()

    for source in sources:
        if isinstance(source, GithubSource):
            facade = GitHubFacade(source.repo, authentication.github_token)
            try:
                for entry in iterate_github_source(directory, source, facade):
                    if (
                        entry.type == DirectoryEntryType.DIRECTORY
                        or entry.type == DirectoryEntryType.LINKED_SOURCE
                    ):
                        if entry.name in seen_directories:
                            continue
                        seen_directories.add(entry.name)
                    yield entry
                continue
            except IncorrectDirectoryException:
                pass

        if utf8_dirname(source.path) != directory:
            continue

        entry = make_directory_entry(directory, source)

        if (
            entry.type == DirectoryEntryType.DIRECTORY
            or entry.type == DirectoryEntryType.LINKED_SOURCE
        ):
            if entry.name in seen_directories:
                continue
            seen_directories.add(entry.name)
        yield entry


def list_project_virtual_directory(
    project: Project,
    directory: typing.Optional[str],
    authentication: LinkedSourceAuthentication,
    only_file_sources: bool = False,
) -> typing.List[DirectoryListEntry]:
    """
    Generate a list of `SourceItem`s for all the `Source`s that belong to a `Project`, in the given `directory`.

    If `directory` is `None` then list the 'root' directory.
    """
    if only_file_sources:
        sources = project.sources.instance_of(FileSource)
    else:
        sources = project.sources.not_instance_of(FileSource)

    return sorted(list(sources_in_directory(directory, sources, authentication)))


def recursive_directory_list(
    project: Project,
    directory: typing.Optional[str],
    authentication: LinkedSourceAuthentication,
) -> typing.Iterable[DirectoryListEntry]:
    for entry in list_project_virtual_directory(project, directory, authentication):
        path = utf8_path_join(directory or "", entry.name)
        if entry.is_directory:
            yield from recursive_directory_list(project, path, authentication)
        yield entry


def os_dir_entry_to_directory_list_entry(
    virtual_path: str, dir_entry: os.DirEntry
) -> DirectoryListEntry:
    """Convert an `os.DirEntry` instance to a `DirectoryListEntry`."""
    s: os.stat_result = dir_entry.stat()

    return DirectoryListEntry(
        dir_entry.name.decode("utf8"),
        utf8_path_join(virtual_path, dir_entry.name),
        DirectoryEntryType.DIRECTORY if dir_entry.is_dir() else DirectoryEntryType.FILE,
        DiskSource(),
        datetime.datetime.fromtimestamp(s.st_mtime),
    )


def list_project_filesystem_directory(
    project_storage_root: str,
    project: Project,
    relative_directory: typing.Optional[str],
) -> typing.List[DirectoryListEntry]:
    """List the directory `relative_directory`, which is relative to the `Project`'s storage root."""
    relative_directory = relative_directory or ""
    directory_to_list = get_filesystem_project_path(
        project_storage_root, project, relative_directory
    )

    if not utf8_isdir(directory_to_list):
        return []

    return directory_entries(directory_to_list, relative_directory)


def directory_entries(directory_to_list: str, relative_directory: str) -> typing.List:
    """
    List the directory at `directory_to_list` and then return a list of `DirectoryListEntry`'s.

    The entries are sorted with directories first, then alphabetically. The `relative_directory` argument is required to
    build a path to the item for end-user consumption (i.e. the full path will be what the user should see, not the
    actual full path on disk).
    """
    return sorted(
        list(
            map(
                functools.partial(
                    os_dir_entry_to_directory_list_entry, relative_directory
                ),
                utf8_scandir(directory_to_list),
            )
        )
    )


def list_snapshot_directory(
    snapshot: Snapshot, relative_directory: typing.Optional[str]
) -> typing.List[DirectoryListEntry]:
    """Generate a list of files in the directory `relative_directory`, relative to the `snapshot` root."""
    relative_directory = relative_directory or ""
    directory_to_list = snapshot_path(snapshot, relative_directory)
    if not utf8_isdir(directory_to_list):
        return []
    return directory_entries(directory_to_list, relative_directory)


def get_filesystem_project_path(
    project_storage_root: str, project: Project, relative_path: str
) -> str:
    """
    Get the path of a file relative to the `Project`'s storage directory.

    If path traversal is attempted (e.g. relative path contains '/../') then an OSError is raised.
    """
    project_storage_directory = utf8_realpath(
        generate_project_storage_directory(project_storage_root, project)
    )
    project_path = utf8_realpath(
        utf8_path_join(project_storage_directory, relative_path)
    )
    if not path_is_in_directory(project_path, project_storage_directory, True):
        raise OSError("Attempting to access path outside of project root.")
    return project_path


def snapshot_path(snapshot: Snapshot, relative_path: str) -> str:
    """
    Get the path of a file relative to the `Snapshot`'s  directory.

    If path traversal is attempted (e.g. relative path contains '/../' then an OSError is raised.
    """
    snapshot_real_path = utf8_realpath(snapshot.path)
    full_path = utf8_realpath(utf8_path_join(snapshot_real_path, relative_path))
    if not path_is_in_directory(full_path, snapshot_real_path, True):
        raise OSError("Attempting to access path outside of project root.")
    return full_path


def combine_virtual_and_real_entries(
    virtual_files: typing.List[DirectoryListEntry],
    real_files: typing.List[DirectoryListEntry],
) -> typing.List[DirectoryListEntry]:
    """
    Combine a list of virtual on real files with virtual files taking precedence over real.

    A real file should only be show in the list of files if it is not already represented by a virtual file (`Source`).

    The reason for this is that after a pull (e.g. from Github) the files will exist on disk but we won't know where
    they come from unless we can relate back to the `Source`.
    """
    name_getter = attrgetter("name")
    virtual_names = list(map(name_getter, virtual_files))

    return sorted(
        virtual_files
        + list(filter(lambda e: name_getter(e) not in virtual_names, real_files))
    )


def path_entry_iterator(
    path: typing.Optional[str] = "", root_name: str = "Files"
) -> typing.Iterable[PathEntry]:
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
    path = path or ""
    yield PathEntry(root_name, "")

    if path:
        split_path = list(filter(lambda component: component != ".", path.split("/")))

        for i, name in enumerate(split_path):
            full_path = "/".join(split_path[: i + 1])
            yield PathEntry(split_path[i], full_path)
