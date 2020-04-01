import datetime
from operator import attrgetter
from unittest import mock

from django.test import TestCase

from lib.path_operations import normalise_path, path_is_in_directory
from projects.source_item_models import DirectoryListEntry, DirectoryEntryType
from projects.source_models import (
    Source,
    FileSource,
    GithubSource,
    LinkedSourceAuthentication,
)
from projects.source_operations import (
    sources_in_directory,
    path_entry_iterator,
    strip_directory,
    determine_entry_type,
    list_linked_source_directory,
    IncorrectDirectoryException,
    iterate_github_source,
    make_directory_entry,
)


class NormalisePathTest(TestCase):
    """Test the behaviour of the `normalise_path` function."""

    def test_normalise_current_directory(self):
        """Passing in `.` should always return '' regardless of `append_slash` flag."""
        self.assertEqual("", normalise_path(".", False))
        self.assertEqual("", normalise_path(".", True))

    def test_normalise_empty_path(self):
        """Passing in `` should always return '' regardless of `append_slash` flag."""
        self.assertEqual("", normalise_path("", False))
        self.assertEqual("", normalise_path("", True))

    def test_slash_append_path_with_slash(self):
        """
        If the path passed in already has a slash at the end, no extra slash should be appended, regardless of the
        `append_slash` flag.
        """
        self.assertEqual("some/path/", normalise_path("some/path/", False))
        self.assertEqual("some/path/", normalise_path("some/path/", True))

    def test_slash_append_path_without_slash(self):
        """If the path passed in has no slash at the end, add an extra slash based on the `append_slash` flag."""
        self.assertEqual("some/path", normalise_path("some/path", False))
        self.assertEqual("some/path/", normalise_path("some/path", True))


class PathIsInDirectoryTest(TestCase):
    """Test the behaviour of the `path_is_in_directory` function."""

    def test_path_in_directory(self):
        """It should return True if a path is inside a directory."""
        self.assertTrue(path_is_in_directory("path/to/file", "path/to/"))

    def test_path_not_in_directory(self):
        """It should return False if a path is not inside a directory."""
        self.assertFalse(path_is_in_directory("path/to/file", "different/path"))
        self.assertFalse(path_is_in_directory("path/to/file", "different/to/f"))


class StripDirectoryTest(TestCase):
    """Test the behaviour of the `strip_directory` function."""

    def test_strip_directory_normal(self):
        """Test the normal behaviour of using `strip_directory` with a number of scenarios."""
        self.assertEqual("file", strip_directory("path/to/thing/file", "path/to/thing"))
        self.assertEqual(
            "file", strip_directory("path/to/thing/file", "path/to/thing/")
        )

    def test_strip_directory_failure(self):
        """If a path is not inside a directory, ValueError should be raised."""
        with self.assertRaises(ValueError):
            strip_directory("path/to/file", "another/directory")

        with self.assertRaises(ValueError):
            strip_directory("path/to/file", "/path/to/f")


class DetermineEntryTypeTest(TestCase):
    """Test behaviour of `determine_entry_type` function."""

    def test_determine_file(self):
        """An entry should be considered a file if its source is a FileSource and there is no / in its name."""
        self.assertEqual(
            DirectoryEntryType.FILE, determine_entry_type(FileSource(), "name")
        )

    def test_determine_directory(self):
        """An entry should be considered a directory if its source is a FileSource and there is a / in its name."""
        self.assertEqual(
            DirectoryEntryType.DIRECTORY,
            determine_entry_type(FileSource(), "long/path"),
        )

    def test_determine_linked(self):
        """An entry should be considered a linked source if its source is not FileSource."""
        self.assertEqual(
            DirectoryEntryType.LINKED_SOURCE,
            determine_entry_type(GithubSource(), "long/path"),
        )
        self.assertEqual(
            DirectoryEntryType.LINKED_SOURCE,
            determine_entry_type(GithubSource(), "name"),
        )


class LinkedSourceDirectoryListTest(TestCase):
    """
    Test behaviour of `list_linked_source_directory` function. Currently only listing of `GithubSource` is supported.
    """

    def test_list_not_github(self):
        """A `TypeError` should be raised if trying to list a source that is not a `GitHubSource`."""
        with self.assertRaises(TypeError):
            # wrap with list otherwise the function won't be called as it is an iterator
            list(list_linked_source_directory(FileSource(), "any/path"))

    def test_list_github_source_no_facade(self):
        """Listing a github source should fail if no facade is passed in."""
        with self.assertRaises(TypeError):
            # wrap with list otherwise the function won't be called as it is an iterator
            list(list_linked_source_directory(GithubSource(), "any/path"))

    def test_list_github_source(self):
        """
        Listing a github source should create a `DirectoryListEntry` for each item returned by
        `GitHubFacade.list_directory`.
        """
        file_edit_date = datetime.datetime(2019, 12, 25, 10, 5, 4)
        directory_edit_date = datetime.datetime(2018, 10, 4, 6, 2, 1)

        facade = mock.MagicMock()
        facade.list_directory.return_value = [
            ("file", False, file_edit_date),
            ("directory", True, directory_edit_date),
        ]

        source = GithubSource()
        source.subpath = "subpath"
        source.path = "mapped"

        entries = list(list_linked_source_directory(source, "any/path", facade))

        facade.list_directory.assert_called_with("subpath/any/path")

        self.assertEqual(2, len(entries))

        self.assertIsInstance(entries[0], DirectoryListEntry)
        self.assertEqual(DirectoryEntryType.FILE, entries[0].type)
        self.assertEqual("mapped/any/path/file", entries[0].path)
        self.assertEqual(file_edit_date, entries[0].modification_date)
        self.assertEqual(source, entries[0].source)

        self.assertIsInstance(entries[1], DirectoryListEntry)
        self.assertEqual(DirectoryEntryType.DIRECTORY, entries[1].type)
        self.assertEqual("mapped/any/path/directory", entries[1].path)
        self.assertEqual(directory_edit_date, entries[1].modification_date)
        self.assertEqual(source, entries[1].source)


class TestIterateGithubSource(TestCase):
    """Test the behaviour of the `iterate_github_source` function."""

    def test_iterate_github_source_incorrect_directory(self):
        """
        If `iterate_github_source` is called with a source that is not inside the directory passed in, an
        `IncorrectDirectoryException` should be raised.
        """
        source = GithubSource()
        source.path = "some/bad/path"

        with self.assertRaises(IncorrectDirectoryException):
            list(iterate_github_source("a/different/path", source, mock.MagicMock()))

    @mock.patch("projects.source_operations.list_linked_source_directory")
    def test_iterate_github_source_current_directory(self, mock_llsd):
        """
        If `iterate_github_source` is called with a source that matches the current directory, then the root repository
        directory should be listed.
        """
        source = GithubSource()
        source.path = "."
        facade = mock.MagicMock()

        mock_llsd.return_value = [("file", False), ("directory", True)]

        entries = list(iterate_github_source("", source, facade))

        mock_llsd.assert_called_with(source, "", facade)

        self.assertEqual(2, len(entries))

        self.assertEqual("file", entries[0][0])
        self.assertFalse(entries[0][1])

        self.assertEqual("directory", entries[1][0])
        self.assertTrue(entries[1][1])

    @mock.patch("projects.source_operations.list_linked_source_directory")
    def test_iterate_github_source_directory(self, mock_llsd):
        """
        If `iterate_github_source` is called with a source inside the current directory, then the relative directory
        should be listed.
        """
        source = GithubSource()
        source.path = "path/in/project"
        facade = mock.MagicMock()

        mock_llsd.return_value = [("directory2", True), ("file2", False)]

        entries = list(iterate_github_source("path/in/project", source, facade))

        mock_llsd.assert_called_with(source, "", facade)

        self.assertEqual(2, len(entries))

        self.assertEqual("directory2", entries[0][0])
        self.assertTrue(entries[0][1])

        self.assertEqual("file2", entries[1][0])
        self.assertFalse(entries[1][1])


class MakeDirectoryEntryTest(TestCase):
    """Test the behavior of the `make_directory_entry` function."""

    def test_make_file_directory_entry(self):
        """
        Test that if a file path is passed in to `make_directory_entry`, the filename (last path component) is parsed
        and the type is FILE.
        """
        source = FileSource()
        source.path = "path/to/file.py"

        de = make_directory_entry("path/to", source)

        self.assertIsInstance(de, DirectoryListEntry)
        self.assertEqual(DirectoryEntryType.FILE, de.type)
        self.assertEqual("file.py", de.name)
        self.assertEqual(de.source, source)

    def test_make_directory_directory_entry(self):
        """
        Test that if a directory path is passed in to `make_directory_entry`, the directory name (first path component
        after the passed in directory) is parsed and the type is DIRECTORY.
        """
        source = FileSource()
        source.path = "path/to/directory/file2/py"

        de = make_directory_entry("path/to", source)

        self.assertIsInstance(de, DirectoryListEntry)
        self.assertEqual(DirectoryEntryType.DIRECTORY, de.type)
        self.assertEqual("directory", de.name)
        self.assertEqual(de.source, source)


def mock_ghs_iterator(path, source, facade):
    if source.path == "bad/path":
        raise IncorrectDirectoryException

    ghs_return_mock = mock.MagicMock()
    ghs_return_mock.name = source.path.split("/")[-1]
    ghs_return_mock.ghs_id = "ghs_iterator_good_return_" + source.path
    ghs_return_mock.type = DirectoryEntryType.DIRECTORY
    yield ghs_return_mock


class SourcesInDirectoryTest(TestCase):
    """Test the behaviour of the `sources_in_directory` function."""

    @mock.patch("projects.source_operations.GitHubFacade")
    @mock.patch(
        "projects.source_operations.iterate_github_source",
        side_effect=mock_ghs_iterator,
    )
    def test_sources_in_directory_happy_path(self, mock_igs, mock_ghf_init):
        """
        Extensive test using mocks to make sure that:
        a) only sources inside the current directory are processed
        b) `GithubSource`s are handled by github functions
        c) Github authorization tokens are passed in
        d) `FileSource`s are handled by generating a DirectoryEntry
        """
        github_source_1 = GithubSource(path="good/path", repo="user/goodrepo")
        github_source_2 = GithubSource(path="bad/path", repo="user/badrepo")
        github_source_3 = GithubSource(path="good/path/three", repo="user/goodrepo")

        file_source_1 = FileSource(path="good/path/file.py")
        file_source_2 = FileSource(path="bad/path/file2.py")
        file_source_3 = FileSource(path="good/path/three/file2.py")

        sources = [
            github_source_1,
            file_source_1,
            github_source_2,
            file_source_2,
            github_source_3,
            file_source_3,
        ]

        dir_list = list(
            sources_in_directory(
                "good/path", sources, LinkedSourceAuthentication("abc123")
            )
        )

        mock_igs.assert_any_call(
            "good/path", github_source_1, mock_ghf_init.return_value
        )
        mock_igs.assert_any_call(
            "good/path", github_source_2, mock_ghf_init.return_value
        )
        mock_ghf_init.assert_any_call("user/goodrepo", "abc123")
        mock_ghf_init.assert_any_call("user/badrepo", "abc123")

        # Github sources show as directories
        self.assertEqual("ghs_iterator_good_return_good/path", dir_list[0].ghs_id)
        self.assertEqual("path", dir_list[0].name)
        self.assertEqual(DirectoryEntryType.DIRECTORY, dir_list[0].type)

        self.assertEqual("file.py", dir_list[1].name)
        self.assertEqual(DirectoryEntryType.FILE, dir_list[1].type)

        # Directories inside github sources show as directories (although it's kind of nebulous as they could be
        # virtually generated)
        self.assertEqual("three", dir_list[2].name)
        self.assertEqual("ghs_iterator_good_return_good/path/three", dir_list[2].ghs_id)
        self.assertEqual(DirectoryEntryType.DIRECTORY, dir_list[2].type)


def source_from_id_and_path(id: int, path: str) -> mock.MagicMock:
    s = mock.MagicMock(spec=Source, name="Source for {}".format(path))
    s.id = id
    s.path = path
    return s


class DirectoryListingTest(TestCase):
    """Test the behaviour of functions that operate on Sources."""

    def setUp(self):
        paths = ["file", "dir/file2", "dir/dir3/otherfile", "dir2/file.csv", "file2"]
        self.sources = list(
            map(
                lambda id_path: source_from_id_and_path(id_path[0], id_path[1]),
                enumerate(paths),
            )
        )

    def test_sorting(self):
        """Test the sorting of a list of `DirectoryListEntry`ies. Directories first, and then alphabetical."""
        s = Source()

        directory_entries = [
            DirectoryListEntry("a", "path/a", DirectoryEntryType.FILE, s),
            DirectoryListEntry("b", "path/b", DirectoryEntryType.LINKED_SOURCE, s),
            DirectoryListEntry("c", "path/c", DirectoryEntryType.DIRECTORY, s),
            DirectoryListEntry("d", "path/d", DirectoryEntryType.LINKED_SOURCE, s),
            DirectoryListEntry("e", "path/e", DirectoryEntryType.FILE, s),
            DirectoryListEntry("f", "path/f", DirectoryEntryType.DIRECTORY, s),
        ]

        """
        Result should be:
        DirectoryListEntry('c', 'path/c', DirectoryEntryType.DIRECTORY, s)
        DirectoryListEntry('f', 'path/f', DirectoryEntryType.DIRECTORY, s)
        DirectoryListEntry('b', 'path/b', DirectoryEntryType.LINKED_SOURCE, s)
        DirectoryListEntry('d', 'path/d', DirectoryEntryType.LINKED_SOURCE, s)
        DirectoryListEntry('a', 'path/a', DirectoryEntryType.FILE, s)
        DirectoryListEntry('e', 'path/e', DirectoryEntryType.FILE, s)
        """
        sorted_entries = sorted(directory_entries)
        self.assertEqual(list("cfbdae"), list(map(attrgetter("name"), sorted_entries)))
        self.assertEqual(
            [
                DirectoryEntryType.DIRECTORY,
                DirectoryEntryType.DIRECTORY,
                DirectoryEntryType.LINKED_SOURCE,
                DirectoryEntryType.LINKED_SOURCE,
                DirectoryEntryType.FILE,
                DirectoryEntryType.FILE,
            ],
            list(map(attrgetter("type"), sorted_entries)),
        )

    def test_path_entry_iterator_no_directory(self):
        """Calling `path_entry_iterator` with None or '' argument should yield just the root `PathEntry`."""
        path_entries = list(path_entry_iterator(None))
        self.assertEqual(1, len(path_entries))
        self.assertEqual("", path_entries[0].path)
        self.assertEqual("Files", path_entries[0].name)

        path_entries = list(path_entry_iterator(""))
        self.assertEqual(1, len(path_entries))
        self.assertEqual("", path_entries[0].path)
        self.assertEqual("Files", path_entries[0].name)

    def test_path_entry_iterator_single_level(self):
        """
        Calling `path_entry_iterator` with a single directory argument should yield the root `PathEntry` and the one
        directory.
        """
        path_entries = list(path_entry_iterator("dir"))
        self.assertEqual(2, len(path_entries))

        self.assertEqual("", path_entries[0].path)
        self.assertEqual("Files", path_entries[0].name)

        self.assertEqual("dir", path_entries[1].path)
        self.assertEqual("dir", path_entries[1].name)

    def test_path_entry_iterator_multi_level(self):
        """
        Calling `path_entry_iterator` with a multi-level directory argument should yield the root `PathEntry` and all
        other directories.
        """
        path_entries = list(path_entry_iterator("dir/level2/level3/foo"))
        self.assertEqual(5, len(path_entries))

        self.assertEqual("", path_entries[0].path)
        self.assertEqual("Files", path_entries[0].name)

        self.assertEqual("dir", path_entries[1].path)
        self.assertEqual("dir", path_entries[1].name)

        self.assertEqual("dir/level2", path_entries[2].path)
        self.assertEqual("level2", path_entries[2].name)

        self.assertEqual("dir/level2/level3", path_entries[3].path)
        self.assertEqual("level3", path_entries[3].name)

        self.assertEqual("dir/level2/level3/foo", path_entries[4].path)
        self.assertEqual("foo", path_entries[4].name)
