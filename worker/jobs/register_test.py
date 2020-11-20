import os
from datetime import datetime

import pytest
from stencila.schema.json import object_encode
from stencila.schema.types import Article, CreativeWork, Person, PropertyValue, Review

from .register import Register

# These tests use a `pytest-recording` "casette" to record resposes from https://test.crossref.org/
# Those casettes has had any sensitive data redacted from them.
# To re-record casettes do
#  CROSSREF_API_CREDENTIALS=username:password ./venv/bin/pytest --record-mode=rewrite jobs/register_test.py

# Pretend these credentials have been set so that we can reuse the
# recorded casettes
credentials = os.getenv("CROSSREF_API_CREDENTIALS", "username:password")


def is_isodate(value: str) -> bool:
    """Test that a string is a valid ISO date."""
    return isinstance(datetime.fromisoformat(value.replace("Z", "+00:00")), datetime)


@pytest.mark.vcr
def test_register_article():
    """
    Test registration of an Article.
    """
    article = object_encode(
        Article(
            authors=[object_encode(Person(givenNames=["Joe"], familyNames=["James"]))],
            title="My preprint",
        )
    )

    job = Register(
        server="https://test.crossref.org/servlet/deposit", credentials=credentials
    )
    result = job.do(
        node=article,
        doi="10.47704/54320",
        url="https://example.org",
        batch="the-unique-batch-id",
    )

    assert isinstance(result, dict)
    assert is_isodate(result["deposited"])
    assert isinstance(result["deposit_request"], dict)
    assert isinstance(result["deposit_response"], dict)
    assert result["deposit_success"]


@pytest.mark.vcr
def test_register_review():
    """
    Test registration of a Review.
    """
    review = object_encode(
        Review(
            authors=[object_encode(Person(givenNames=["Joe"], familyNames=["James"]))],
            title="Review of my preprint",
            itemReviewed=object_encode(
                Article(
                    identifiers=[
                        object_encode(PropertyValue(name="doi", value="10.5555/54320"))
                    ]
                )
            ),
        )
    )

    job = Register(
        server="https://test.crossref.org/servlet/deposit", credentials=credentials
    )
    result = job.do(
        node=review,
        doi="10.47704/54321",
        url="https://example.org",
        batch="the-unique-batch-id",
    )

    assert isinstance(result, dict)
    assert is_isodate(result["deposited"])
    assert isinstance(result["deposit_request"], dict)
    assert isinstance(result["deposit_response"], dict)
    assert result["deposit_success"]


@pytest.mark.vcr
def test_bad_credentials():
    """
    Test incorrect credentials error.
    """
    job = Register(
        server="https://test.crossref.org/servlet/deposit", credentials="foo:bar"
    )
    result = job.do(
        node=object_encode(Article()),
        doi="10.5555/54321",
        url="https://example.org",
        batch="the-unique-batch-id",
    )

    assert isinstance(result, dict)
    assert is_isodate(result["deposited"])
    assert isinstance(result["deposit_request"], dict)
    assert isinstance(result["deposit_response"], dict)
    assert not result["deposit_success"]


def test_no_credentials():
    """
    Test no credentials error.
    """
    if "CROSSREF_API_CREDENTIALS" in os.environ:
        del os.environ["CROSSREF_API_CREDENTIALS"]
    job = Register(server="https://test.crossref.org/servlet/deposit")
    result = job.do(
        node=object_encode(Article()),
        doi="10.5555/54321",
        url="https://example.org",
        batch="the-unique-batch-id",
    )
    assert isinstance(result, dict)
    assert len(result.keys()) == 0
