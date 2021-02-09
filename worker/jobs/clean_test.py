import os

from util.files import list_files
from util.working_directory import working_directory

from .clean import Clean


def test_clean(tempdir):
    with working_directory(tempdir.path):
        assert list_files() == {}

        open("a.txt", "w").write("a")
        open("b.txt", "w").write("b")
        os.mkdir("c")
        open("c/d.txt", "w").write("d")
        os.mkdir("c/e")
        open("c/e/f.txt", "w").write("f")

        assert sorted(list_files().keys()) == ["a.txt", "b.txt", "c/d.txt", "c/e/f.txt"]
        assert sorted(os.listdir()) == ["a.txt", "b.txt", "c"]

        files = Clean().do()

        assert files == {}
        assert os.listdir() == []
