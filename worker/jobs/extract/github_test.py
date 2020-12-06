import os

import pytest
from stencila.schema.types import Comment, Review

from .github import extract_github


@pytest.mark.vcr
def test_get_review():
    review = extract_github(
        source=dict(repo="stencila/test"),
        filters=dict(pr_number=1, review_id=541396696),
    )
    assert isinstance(review, Review)
    assert len(review.authors) == 1
    assert review.authors[0].name == "Nokome Bentley"
    assert review.dateCreated == "2020-12-01T00:19:44"
    assert review.content == [
        dict(type="Paragraph", content=["Another test PR review having two comments."])
    ]

    assert len(review.comments) == 2

    comment1 = review.comments[0]
    assert comment1.authors[0].name == "Nokome Bentley"
    assert comment1.content == ["A test PR review comment."]
    assert comment1.commentAspect == "document.md#L3"

    comment1 = review.comments[1]
    assert comment1.authors[0].name == "Nokome Bentley"
    assert comment1.content == ["Another test PR review comment."]
