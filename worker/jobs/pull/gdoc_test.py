import os
import pytest

from .gdoc import pull_gdoc

# The following access token is expired, but was valid when this test
# was recorded. To re-record this test, get a new google token, and
# ensure that the google account has access to any docs and drive
# folders required.

GOOGLE_TOKEN = (
    "ya29.a0AfH6SMDJdyz151yBr4hQa8xNwCkUW5SNjK_LVQ6B21Rpius4sQOK6oDNEm7yYXG3_tf"
    "fXM8dq1Z2k65zfZQ37FzYeVygEp93LB4_8gHEr1BDb9rZarmqjCoVUBoSOzyns1bHGYH_T15ka"
    "O945eax1aJGZCR4vfYFNmyO"
)


def test_missing_token(tempdir):
    doc_id = "1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA"
    with pytest.raises(AssertionError) as excinfo:
        pull_gdoc(dict(doc_id=doc_id), tempdir.path, "{}.json".format(doc_id))
    assert "A Google authentication token is required" in str(excinfo.value)


@pytest.mark.vcr
def test_ok(tempdir):
    doc_id = "14z9ScjW4gVjPBRw5XfIdA5LxrApUJx3-S7cXgdNvElc"
    doc_json = "{}.json".format(doc_id)
    pull_gdoc(
        dict(doc_id=doc_id, token=GOOGLE_TOKEN,), tempdir.path, doc_json,
    )
    assert os.path.exists(os.path.join(tempdir.path, doc_json))
