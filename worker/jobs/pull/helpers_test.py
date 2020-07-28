import os
from pathlib import Path
import pytest

from .helpers import begin_pull, end_pull


def test_begin_end_pull(tempdir):
    working = tempdir.path

    # Simulate some files in the working dir
    # that are not part of the pull (in other subpaths)
    os.makedirs(os.path.join(working, "b"))
    with open(os.path.join(working, "c.txt"), "w") as file:
        file.write("another file")

    # Begin the pull
    temporary = begin_pull(working)
    assert isinstance(temporary, str)

    # Simulate the pulling of files into the temporary
    # directory
    for path, size in [
        ("a.txt", 1),
        ("a.tar.gz", 2),
        ("a.media/c.html", 10),
        ("a.media/d.foo", 100),
    ]:
        full_path = os.path.join(temporary, path)
        Path(full_path).parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as file:
            file.write(b"a" * size)

    # End the pull
    files = end_pull(working, "a", temporary)

    # Check there is a modification time and fingerprint 
    # for each file but remove them for assertion below
    # to be deterministic
    for path in files.keys():
        assert files[path]["modified"]
        del files[path]["modified"]
        assert files[path]["fingerprint"]
        del files[path]["fingerprint"]

    assert files == {
        "a.txt": {"encoding": None, "mimetype": "text/plain", "size": 1},
        "a.tar.gz": {"encoding": "gzip", "mimetype": "application/x-tar", "size": 2},
        "a.media/c.html": {"encoding": None, "mimetype": "text/html", "size": 10},
        "a.media/d.foo": {"encoding": None, "mimetype": None, "size": 100},
    }

    # The temporary directory should have been removed
    # and the other files should still exist
    tempdir.compare(
        (
            "a.txt",
            "a.tar.gz",
            "a.media/",
            "a.media/c.html",
            "a.media/d.foo",
            "b/",
            "c.txt",
        )
    )
