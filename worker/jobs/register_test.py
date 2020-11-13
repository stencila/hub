from datetime import datetime

import pytest
from stencila.schema.json import object_encode
from stencila.schema.types import Article, CreativeWork

from .register import Register

# These tests use a `pytest-recording` "casette" to record resposes from https://test.crossref.org/
# Those casettes has had any sensitive data redacted from them.
# To re-record casettes do
#  CROSSREF_API_CREDENTIALS=username:password ./venv/bin/pytest --record-mode=rewrite jobs/register_test.py

# TODO: Import Review directly when it is available


def Review(*args, **kwargs):
    work = CreativeWork(*args, **kwargs)
    work.type = "Review"
    return work


def is_isodate(value: str) -> bool:
    """Test that a string is a valid ISO date."""
    return isinstance(datetime.fromisoformat(value.replace("Z", "+00:00")), datetime)


@pytest.mark.skip("Only works with https://github.com/stencila/encoda/pull/754.")
@pytest.mark.vcr
def test_register_article():
    """
    Test registration of an Article.
    """
    job = Register(server="https://test.crossref.org/servlet/deposit")
    result = job.do(
        node=object_encode(Article()), doi="10.5555/54321", url="https://example.org"
    )

    assert isinstance(result, dict)
    assert is_isodate(result["deposited"])
    assert is_isodate(result["registered"])
    assert isinstance(result["request"], dict)
    assert isinstance(result["response"], dict)


@pytest.mark.skip(
    "Requires https://github.com/stencila/schema/issues/228 to be in Encoda for Review schema."
)
@pytest.mark.vcr
def test_register_review():
    """
    Test registration of a Review.
    """
    job = Register(server="https://test.crossref.org/servlet/deposit")
    result = job.do(
        node=object_encode(Review()), doi="10.5555/54321", url="https://example.org"
    )

    assert isinstance(result, dict)
    assert is_isodate(result["deposited"])
    assert is_isodate(result["registered"])
    assert isinstance(result["request"], dict)
    assert isinstance(result["response"], dict)


@pytest.mark.vcr
def test_bad_credentials():
    """
    Test incorrect credentials error.
    """
    job = Register(
        server="https://test.crossref.org/servlet/deposit", credentials="foo:bar"
    )
    result = job.do(
        node=object_encode(Article()), doi="10.5555/54321", url="https://example.org"
    )

    assert isinstance(result, dict)
    assert is_isodate(result["deposited"])
    assert result["registered"] is None
    assert isinstance(result["request"], dict)
    assert isinstance(result["response"], dict)


def test_no_credentials():
    """
    Test no credentials error.
    """
    job = Register(server="https://test.crossref.org/servlet/deposit", credentials="")
    with pytest.raises(PermissionError) as excinfo:
        job.do(
            node=object_encode(Article()),
            doi="10.5555/54321",
            url="https://example.org",
        )
        assert "Credentials for DOI registrar are not available" in str(excinfo.value)
