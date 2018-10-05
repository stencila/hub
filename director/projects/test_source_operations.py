from operator import attrgetter
from unittest import mock

from django.test import TestCase

from projects.source_models import Source
from projects.source_operations import sources_in_directory, SourcePath, path_entry_iterator


def source_from_id_and_path(id: int, path: str) -> mock.MagicMock:
    s = mock.MagicMock(spec=Source, name='Source for {}'.format(path))
    s.id = id
    s.path = path
    return s


class DirectoryListingTest(TestCase):
    """Test the behaviour of functions that operate on Sources."""

    def setUp(self):
        paths = [
            'file',
            'dir/file2',
            'dir/dir3/otherfile',
            'dir2/file.csv',
            'file2'
        ]
        self.sources = list(map(lambda id_path: source_from_id_and_path(id_path[0], id_path[1]), enumerate(paths)))

    def test_root_directory_list(self):
        """Test that items in root directory are filtered correctly. Multiple entries sharing the same root dir should
        not appear in the list twice, and directories and files should be marked as such."""
        source_paths = list(sources_in_directory(None, self.sources))

        self.assertEqual(4, len(source_paths))

        self.assertEqual('file', source_paths[0].name)
        self.assertFalse(source_paths[0].is_directory)

        self.assertEqual('dir', source_paths[1].name)
        self.assertTrue(source_paths[1].is_directory)

        self.assertEqual('dir2', source_paths[2].name)
        self.assertTrue(source_paths[2].is_directory)

        self.assertEqual('file2', source_paths[3].name)
        self.assertFalse(source_paths[3].is_directory)

    def test_first_level_directory_list(self):
        """Test listing of first level directory."""
        source_paths = list(sources_in_directory('dir', self.sources))

        self.assertEqual(2, len(source_paths))

        self.assertEqual('file2', source_paths[0].name)
        self.assertFalse(source_paths[0].is_directory)

        self.assertEqual('dir3', source_paths[1].name)
        self.assertTrue(source_paths[1].is_directory)

    def test_second_level_directory_list(self):
        """Test listing of second level directory."""
        source_paths = list(sources_in_directory('dir/dir3', self.sources))

        self.assertEqual(1, len(source_paths))

        self.assertEqual('otherfile', source_paths[0].name)
        self.assertFalse(source_paths[0].is_directory)

    def test_directory_no_match(self):
        """If we try to list a directory that is not in the sources list, the list matching paths should be empty."""
        source_paths = list(sources_in_directory('nomatch', self.sources))
        self.assertEqual(0, len(source_paths))

    def test_list_directory_match(self):
        """
        If for some reason the `directory` argument matches exactly a path, it should not be in the list of returned
        `SourcePath`s.
        """

        source_paths = list(sources_in_directory('dir/file2', self.sources))
        self.assertEqual(0, len(source_paths))

    def test_sorting(self):
        """Test the sorting of a list of `SourcePath`s. Directories first, and then alphabetical."""
        s = Source()

        source_paths = [
            SourcePath(s, 'a', False),
            SourcePath(s, 'd', False),
            SourcePath(s, 'f', True),
            SourcePath(s, 'g', False),
            SourcePath(s, 'b', True),
            SourcePath(s, 'c', False),
            SourcePath(s, 'e', True)
        ]
        """
        Result should be:
        SourcePath(s, 'b', True)
        SourcePath(s, 'e', True)
        SourcePath(s, 'f', True)
        SourcePath(s, 'a', False)
        SourcePath(s, 'c', False)
        SourcePath(s, 'd', False)
        SourcePath(s, 'g', False)
        """
        sorted_paths = sorted(source_paths)
        self.assertEqual(list('befacdg'), list(map(attrgetter('name'), sorted_paths)))
        self.assertEqual([True, True, True, False, False, False, False],
                         list(map(attrgetter('is_directory'), sorted_paths)))

    def test_path_entry_iterator_no_directory(self):
        """Calling `path_entry_iterator` with None or '' argument should yield just the root `PathEntry`."""
        path_entries = list(path_entry_iterator(None))
        self.assertEqual(1, len(path_entries))
        self.assertEqual('', path_entries[0].path)
        self.assertEqual('Files', path_entries[0].name)

        path_entries = list(path_entry_iterator(''))
        self.assertEqual(1, len(path_entries))
        self.assertEqual('', path_entries[0].path)
        self.assertEqual('Files', path_entries[0].name)

    def test_path_entry_iterator_single_level(self):
        """
        Calling `path_entry_iterator` with a single directory argument should yield the root `PathEntry` and the one
        directory.
        """
        path_entries = list(path_entry_iterator('dir'))
        self.assertEqual(2, len(path_entries))

        self.assertEqual('', path_entries[0].path)
        self.assertEqual('Files', path_entries[0].name)

        self.assertEqual('dir', path_entries[1].path)
        self.assertEqual('dir', path_entries[1].name)

    def test_path_entry_iterator_multi_level(self):
        """
        Calling `path_entry_iterator` with a multi-level directory argument should yield the root `PathEntry` and all
        other directories.
        """
        path_entries = list(path_entry_iterator('dir/level2/level3/foo'))
        self.assertEqual(5, len(path_entries))

        self.assertEqual('', path_entries[0].path)
        self.assertEqual('Files', path_entries[0].name)

        self.assertEqual('dir', path_entries[1].path)
        self.assertEqual('dir', path_entries[1].name)

        self.assertEqual('dir/level2', path_entries[2].path)
        self.assertEqual('level2', path_entries[2].name)

        self.assertEqual('dir/level2/level3', path_entries[3].path)
        self.assertEqual('level3', path_entries[3].name)

        self.assertEqual('dir/level2/level3/foo', path_entries[4].path)
        self.assertEqual('foo', path_entries[4].name)
