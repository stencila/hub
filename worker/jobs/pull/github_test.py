import os

import pytest

from util.working_directory import working_directory

from .github import pull_github


@pytest.mark.vcr
def test_public_repo(tempdir):
    with working_directory(tempdir.path):
        pull_github(source=dict(repo="stencila/test", subpath="sub"))

    tempdir.compare(["README.md"])


@pytest.mark.vcr
def test_subdirectory(tempdir):
    path = "a/very/very/deep/sub/directory"

    with working_directory(tempdir.path):
        pull_github(
            source=dict(repo="stencila/test", subpath=""), path=path,
        )

    for expected in (
        ".travis.yml",
        "README.md",
        "document.md",
        "sub/README.md",
    ):
        assert os.path.exists(os.path.join(tempdir.path, path, expected))


@pytest.mark.vcr
def test_single_file(tempdir):
    with working_directory(tempdir.path):
        pull_github(
            source=dict(repo="stencila/test", subpath="sub/README.md"),
            path="sub_README.md",
        )

    assert not os.path.exists(os.path.join(tempdir.path, "README.md"))
    assert not os.path.exists(os.path.join(tempdir.path, "sub/README.md"))
    assert os.path.exists(os.path.join(tempdir.path, "sub_README.md"))
