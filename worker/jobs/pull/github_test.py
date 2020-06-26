import os
import pytest

from .github import pull_github


@pytest.mark.vcr
def test_public_repo(tempdir):
    source = dict(repo="stencila/test", subpath="sub")
    pull_github(source, tempdir.path, "")
    assert os.path.exists(os.path.join(tempdir.path, "README.md"))


@pytest.mark.vcr
def test_subdirectory(tempdir):
    source = dict(repo="stencila/test", subpath="")
    subdir = "a/very/very/deep/sub/directory"
    pull_github(source, tempdir.path, subdir)
    print(os.listdir(tempdir.path))
    for expected in (
        ".travis.yml",
        "README.md",
        "document.md",
        "sub/README.md",
    ):
        assert os.path.exists(os.path.join(tempdir.path, subdir, expected))


@pytest.mark.vcr
def test_single_file(tempdir):
    source = dict(repo="stencila/test", subpath="sub/README.md")
    pull_github(source, tempdir.path, "sub_README.md")
    assert not os.path.exists(os.path.join(tempdir.path, "README.md"))
    assert not os.path.exists(os.path.join(tempdir.path, "sub/README.md"))
    assert os.path.exists(os.path.join(tempdir.path, "sub_README.md"))
