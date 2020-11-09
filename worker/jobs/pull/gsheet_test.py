import os

import pytest

from util.working_directory import working_directory

from .gsheet import pull_gsheet

# To re-record this test, get a new Google token
# (e.g. via https://developers.google.com/oauthplayground),
# ensure that the Google account has access to the sheet,
# and run `./venv/bin/pytest --record-mode=rewrite jobs/pull/gsheet_test.py`

ACCESS_TOKEN = "XXXXX"


def test_missing_token(tempdir):
    with pytest.raises(AssertionError) as excinfo:
        pull_gsheet(source=dict(doc_id="foo"), path="foo.gsheet")
    assert "A Google access token is required" in str(excinfo.value)


@pytest.mark.vcr
def test_ok(tempdir):
    with working_directory(tempdir.path):
        doc_id = "1SzslazJYVi8KYI6sisUmhJujWW5rbzFthVGtvUb3miM"
        doc_json = "{}.json".format(doc_id)

        files = pull_gsheet(
            source=dict(doc_id=doc_id),
            path=doc_json,
            secrets=dict(access_token=ACCESS_TOKEN),
        )

        assert os.path.exists(doc_json)
        assert files[doc_json]["mimetype"] == "application/vnd.google-apps.spreadsheet"
