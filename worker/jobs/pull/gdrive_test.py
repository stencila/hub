import os

import pytest

from util.path_operations import utf8_path_exists, utf8_path_join

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
    source = dict(folder_id="14SEW9vSYDfgCvuyTjwQI6-x-RF3B_s4z", token=GOOGLE_TOKEN)
    pull_gdrive(source, tempdir.path, "")
    for expected in (
        "test-1.txt",
        "sub/test-2.txt",
    ):
        assert utf8_path_exists(utf8_path_join(tempdir.path, expected))
