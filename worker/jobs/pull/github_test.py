import os
import pytest

from .github import pull_github


def test_missing_token(tempdir):
    with pytest.raises(AssertionError) as excinfo:
        pull_github(dict(repo="stencila/hub", subpath=""), tempdir.path, "")
    assert "source must include a token" in str(excinfo.value)


@pytest.mark.vcr
def test_public_repo(tempdir):
    source = dict(repo="stencila/test", subpath="sub", token=None)
    pull_github(source, tempdir.path, "")
    assert os.path.exists(os.path.join(tempdir.path, "README.md"))
