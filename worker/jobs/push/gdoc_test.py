import json
import os
import pytest

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

from jobs.pull.gdoc import pull_gdoc
from jobs.push.gdoc import push_gdoc

# The following access token is expired, but was valid when this test
# was recorded. To re-record this test, get a new google token, and
# ensure that the google account has access to any docs and drive
# folders required.

GOOGLE_TOKEN = (
    "ya29.a0AfH6SMA6mdf7pf1OYLMu24_7hhcpLXjGXkMUvDwtvvEm12xWzEPDjP3It6FBU5PsBia"
    "5rnBVBXrXYXZijcngUpoMW2OF404eM7Owy7Wm9yTDvATrmS3U5xH_mEQ8cm-1HVTHPjQK3pJst"
    "FzpLzn45ODqB3Vg4-UnwfY8"
)


def test_missing_token(tempdir):
    doc_id = "1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA"
    with pytest.raises(AssertionError) as excinfo:
        push_gdoc("{}.json".format(doc_id), tempdir.path, dict(doc_id=doc_id))
    assert "source must include a token" in str(excinfo.value)


@pytest.mark.vcr
def test_ok(tempdir):

    # Make a copy of a test document using the Drive api
    doc_id_0 = "1eVVLtNiNKh3I1n253UHyldUF0VLv_kVERAl-K58J_EI"
    credentials = GoogleCredentials(
        GOOGLE_TOKEN, None, None, None, None, None, "Stencila Hub Client",
    )
    drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    files_resource = drive_service.files()
    doc_id_1 = files_resource.copy(fileId=doc_id_0).execute()["id"]

    # Pull down a local copy of the copy, and extract the revisionId
    doc_json = "{}.json".format(doc_id_1)
    pulled = pull_gdoc(
        dict(doc_id=doc_id_1, token=GOOGLE_TOKEN,), tempdir.path, doc_json,
    )

    path = os.path.join(tempdir.path, list(pulled.keys())[0])
    body = json.loads(open(path, "rb").read())
    revision_id = body["revisionId"]

    firstelem = body["body"]["content"][1]["paragraph"]["elements"][0]
    old_text = firstelem["textRun"]["content"]
    assert old_text == "some test content"
    textlen = len(old_text)

    # Make a change, and save as edited.json
    new_text = "a" * textlen
    edited = os.path.join(tempdir.path, "edited.json")
    body["body"]["content"][1]["paragraph"]["elements"][0]["textRun"][
        "content"
    ] = new_text
    f = open(edited, "w")
    f.write(json.dumps(body))
    f.close()

    # Push the edited document
    push_gdoc([edited], tempdir.path, dict(doc_id=doc_id_1, token=GOOGLE_TOKEN))

    # Make a copy of the edited document. This gets a new docId, and
    # stops pytest-recording from serving the same response as for the
    # unedited doc.
    doc_id_2 = files_resource.copy(fileId=doc_id_1).execute()["id"]

    # Delete the first copy
    files_resource.delete(fileId=doc_id_1).execute()

    # Pull down the copy of the edited document
    pulled = pull_gdoc(
        dict(doc_id=doc_id_2, token=GOOGLE_TOKEN,), tempdir.path, doc_json,
    )

    # Delete the second copy
    files_resource.delete(fileId=doc_id_2).execute()

    # Check that the change is reflected in the newly pulled doc
    path = os.path.join(tempdir.path, list(pulled.keys())[0])
    body = json.loads(open(path, "rb").read())
    assert new_text in str(body)
    assert old_text not in str(body)
    assert revision_id != body["revisionId"]
