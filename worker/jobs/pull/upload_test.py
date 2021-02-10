from pathlib import Path

import pytest

from util.working_directory import working_directory

from .upload import pull_upload


def test_one(tempdir):
    """
    Test that will create new directories if necessary.
    """
    with working_directory(tempdir.path):
        files = pull_upload(dict(path=__file__), "a/b/some.txt")

    assert list(files.keys()) == ["a/b/some.txt"]
    tempdir.compare(["a/", "a/b/", "a/b/some.txt"])


def test_overwrite(tempdir):
    """
    Test that will overwrite any existing files.
    """
    with working_directory(tempdir.path):
        with open("some.txt", "w") as file:
            file.write("wateva")
        assert open("some.txt").read() == "wateva"

        files = pull_upload(dict(path=__file__), "some.txt")
        assert open("some.txt").read().startswith("from pathlib")
    assert list(files.keys()) == ["some.txt"]
    tempdir.compare(["some.txt"])


def test_mergedirs(tempdir):
    """
    Test that will merge with existing directories.
    """
    with working_directory(tempdir.path):
        # A file that may have come from another source
        Path("a/b").mkdir(parents=True, exist_ok=True)
        with open("a/b/other.txt", "w") as file:
            file.write("whateva")
        # Pull an upload source into the same directory
        files = pull_upload(dict(path=__file__), "a/b/some.txt")
    assert list(files.keys()) == ["a/b/some.txt"]
    tempdir.compare(["a/", "a/b/", "a/b/other.txt", "a/b/some.txt"])
