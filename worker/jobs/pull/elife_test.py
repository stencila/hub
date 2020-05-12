import pytest

from .elife import pull_elife


def test_ok(tempdir):
    pull_elife({"article": 45187}, tempdir.getpath("45187.jats.xml"))
    tempdir.compare(["45187.jats.xml"])


def test_missing_article(tempdir):
    with pytest.raises(AssertionError) as excinfo:
        pull_elife({}, "temp.jats.xml")
    assert "source must have an article number" in str(excinfo.value)
