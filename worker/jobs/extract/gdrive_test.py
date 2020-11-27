import os

import pytest
from stencila.schema.types import Comment, Review

from .gdrive import create_review, extract_gdrive, filter_comments

# To re-record this test, get a new Google token (e.g. via https://developers.google.com/oauthplayground),
# paste it in below, ensure that the Google account has access to the documents
# being accessed, and run
#   ./venv/bin/pytest --record-mode=rewrite jobs/extract/gdrive_test.py

ACCESS_TOKEN = "XXXXXXXXXX"


def test_filter_comments():
    comments = [
        dict(author=dict(displayName="Jill Jones")),
        dict(author=dict(displayName="James Jameson")),
    ]
    n = len(comments)

    assert len(filter_comments(comments, filters={})) == n
    assert len(filter_comments(comments, filters={"unknown key": ""})) == n
    assert len(filter_comments(comments, filters={"name": r"^J"})) == n
    assert len(filter_comments(comments, filters={"name": r"^Ji"})) == 1
    assert len(filter_comments(comments, filters={"name": r"^James Jameson$"})) == 1
    assert len(filter_comments(comments, filters={"name": r"^$"})) == 0


def test_no_comments():
    review = create_review([])
    assert review is None


def test_only_empty_comments():
    review = create_review([dict(), dict(content="")])
    assert review is None


def test_no_comment_that_matches_main():
    review = create_review([dict(content="I'm just a lonesome comment")])
    assert review.content[0] == {
        "type": "Paragraph",
        "content": ["I'm just a lonesome comment"],
    }


def test_missing_id():
    with pytest.raises(AssertionError) as excinfo:
        extract_gdrive(source={})
    assert "A Google document or file id is required" in str(excinfo.value)


def test_missing_token():
    with pytest.raises(AssertionError) as excinfo:
        extract_gdrive(source=dict(doc_id="foo"))
    assert "A Google access token is required" in str(excinfo.value)


@pytest.mark.vcr
def test_fixture_2():
    """
    Test on a real Google Doc.

    https://docs.google.com/document/d/1ngLlIJr2SJ15A7Mnb2mg7f8hWePUDzYETjMjTaPoJWM
    """
    review = extract_gdrive(
        source=dict(doc_id="1ngLlIJr2SJ15A7Mnb2mg7f8hWePUDzYETjMjTaPoJWM"),
        secrets=dict(access_token=ACCESS_TOKEN),
    )
    assert isinstance(review, Review)
    assert review.title == 'Review of "A Google Doc test fixture for Stencila"'
    assert review.authors[0].name == "Nokome Bentley"
    assert review.dateCreated == "2020-11-25T23:22:51.811Z"
    assert review.dateModified == "2020-11-26T01:47:09.180Z"
    assert review.content == [
        {
            "type": "Paragraph",
            "content": [
                "Overall, this is a reasonable attempt at creating a tests fixture "
                "for use in testing Stencila's integrations with Google Docs."
            ],
        },
        {"type": "Paragraph", "content": ["My main concerns are:"]},
        {
            "type": "List",
            "items": [
                {
                    "type": "ListItem",
                    "content": [
                        {"type": "Paragraph", "content": ["it is quite boring"]}
                    ],
                },
                {
                    "type": "ListItem",
                    "content": [
                        {
                            "type": "Paragraph",
                            "content": [
                                "what if someone changes the documents, the tests will break!"
                            ],
                        }
                    ],
                },
            ],
            "order": "unordered",
        },
    ]
    assert len(review.comments) == 1

    comment1 = review.comments[0]
    assert comment1.content == ["This is a test second comment in my review."]
    assert comment1.commentAspect == "is a test"
    assert len(comment1.comments) == 1

    comment1_reply1 = comment1.comments[0]
    assert comment1_reply1.content == ["This is a test reply to my second comment."]
