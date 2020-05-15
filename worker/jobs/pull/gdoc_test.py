import pytest

from .gdoc import pull_gdoc


def test_missing_token(tempdir):
    with pytest.raises(AssertionError) as excinfo:
        pull_gdoc(
            dict(doc_id="1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA"),
            tempdir.path,
            "1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA.json",
        )
    assert "source must include a token" in str(excinfo.value)
