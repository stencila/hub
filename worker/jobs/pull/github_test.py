import os
from contextlib import ContextDecorator
from unittest import mock

import pytest

from util.working_directory import working_directory

from .github import pull_github, pull_zip


def mocked_httpx_stream(*args, **kwargs):
    """
    VCR does not like recording HTTPX stream requests so mock it.

    Returns a context manager that mimics that returned by
    httpx.stream for the stencila/test repo.
    """
    return MockedHttpxStreamContext(*args, **kwargs)


class MockedHttpxStreamContext(ContextDecorator):
    def __init__(self, method, url, **kwargs):
        self.url = url

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return self

    def iter_bytes(self):
        if self.url == "https://codeload.github.com/stencila/test/legacy.zip/master":
            archive = "stencila-test-archive.zip"
        else:
            raise ValueError(f"Unmocked repo archive {self.url}")
        return open(
            os.path.join(
                os.path.dirname(__file__), "cassettes", "github_test", archive
            ),
            "rb",
        )


@pytest.mark.vcr
@mock.patch("httpx.stream", side_effect=mocked_httpx_stream)
def test_public_repo(mock_stream, tempdir):
    with working_directory(tempdir.path):
        files = pull_github(source=dict(repo="stencila/test", subpath="sub"))

    assert list(files.keys()) == ["README.md"]

    tempdir.compare(["README.md"])


@pytest.mark.vcr
@mock.patch("httpx.stream", side_effect=mocked_httpx_stream)
def test_subdirectory(mock_stream, tempdir):
    path = "a/very/very/deep/sub/directory"

    with working_directory(tempdir.path):
        files = pull_github(source=dict(repo="stencila/test", subpath=""), path=path,)

    filenames = [
        ".travis.yml",
        "README.md",
        "document.md",
        "sub/README.md",
    ]

    assert sorted(list(files.keys())) == sorted(filenames)

    for expected in filenames:
        assert os.path.exists(os.path.join(tempdir.path, path, expected))


@pytest.mark.vcr
@mock.patch("httpx.stream", side_effect=mocked_httpx_stream)
def test_single_file(mock_stream, tempdir):
    with working_directory(tempdir.path):
        pull_github(
            source=dict(repo="stencila/test", subpath="sub/README.md"),
            path="sub_README.md",
        )

    assert not os.path.exists(os.path.join(tempdir.path, "README.md"))
    assert not os.path.exists(os.path.join(tempdir.path, "sub/README.md"))
    assert os.path.exists(os.path.join(tempdir.path, "sub_README.md"))


def test_large_zip(tempdir):
    with working_directory(tempdir.path):
        zip_file = os.path.join(
            os.path.dirname(__file__), "fixtures", "1000-maniacs.zip"
        )
        files = pull_zip(zip_file, strip=0)

    assert len(files.keys()) == 1000

    info = files.get("1.txt")
    del info["modified"]
    assert info == {
        "encoding": None,
        "fingerprint": "7f8cafc8690f2707d1b7e8a40a59d8299e1af8f862576ba896acaca287fd4006",
        "mimetype": "text/plain",
        "size": 6,
    }


def test_huge_zip(tempdir):
    """
    A performance test using a huge repository archive.

    To run this test, download the Zip file of https://github.com/sophiedeb/logistic_models
    and run this file with:
        ./venv/bin/pytest jobs/pull/githubtest.py --durations=0

    It has 3304 files in it (at time of writing). Before optimizations this too 360s to
    run; after 11s.
    """
    zip_file = os.path.join(
        os.path.dirname(__file__), "fixtures", "logistic_models-master.zip"
    )
    if not os.path.exists(zip_file):
        return

    with working_directory(tempdir.path):
        pull_zip(zip_file)
