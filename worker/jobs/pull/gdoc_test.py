import os

import pytest

from util.working_directory import working_directory

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
    with pytest.raises(AssertionError) as excinfo:
        pull_gdoc(source=dict(doc_id="foo"), path="foo.gdoc")
    assert "A Google access token is required" in str(excinfo.value)


@pytest.mark.vcr
def test_ok(tempdir):
    with working_directory(tempdir.path):
        doc_id = "14z9ScjW4gVjPBRw5XfIdA5LxrApUJx3-S7cXgdNvElc"
        doc_json = "{}.json".format(doc_id)

        files = pull_gdoc(
            source=dict(doc_id=doc_id),
            path=doc_json,
            secrets=dict(access_token=GOOGLE_TOKEN),
        )

        assert os.path.exists(doc_json)
        assert files[doc_json]["mimetype"] == "application/vnd.google-apps.document"
