import os

import pytest

from .gdrive import pull_gdrive

# The following access token is expired, but was valid when this test
# was recorded. To re-record this test, get a new google token, and
# ensure that the google account has access to any docs and drive
# folders required.

GOOGLE_TOKEN = (
    "ya29.a0AfH6SMDJdyz151yBr4hQa8xNwCkUW5SNjK_LVQ6B21Rpius4sQOK6oDNEm7yYXG3_tf"
    "fXM8dq1Z2k65zfZQ37FzYeVygEp93LB4_8gHEr1BDb9rZarmqjCoVUBoSOzyns1bHGYH_T15ka"
    "O945eax1aJGZCR4vfYFNmyO"
)


@pytest.mark.vcr
def test_folder(tempdir):
    pull_gdrive(
        source=dict(kind="folder", google_id="14SEW9vSYDfgCvuyTjwQI6-x-RF3B_s4z"),
        path=tempdir.path,
        secrets=dict(access_token=GOOGLE_TOKEN),
    )

    for expected in (
        "test-1.txt",
        "sub/test-2.txt",
    ):
        assert os.path.exists(os.path.join(tempdir.path, expected))
