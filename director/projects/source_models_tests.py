from django.core.exceptions import ValidationError
from django.db.models import Q
import pytest

from projects.source_models import (
    Source,
    SourceAddress,
    DatSource,
    GithubSource,
    GoogleDocsSource,
    UrlSource,
)


def test_source_address():
    with pytest.raises(KeyError, match='Unknown source type "foo"'):
        SourceAddress("foo")


def test_coerce_address():
    # A specific address (ie. starting with type://)
    sa = Source.coerce_address("github://org/repo/a/file.md")
    assert sa.type == GithubSource
    assert sa["repo"] == "org/repo"
    assert sa["subpath"] == "a/file.md"

    # A HTTP URL that is matched by a specific source
    sa = Source.coerce_address("https://github.com/org/repo")
    assert sa.type == GithubSource

    # A generic URL that caught as a URL source
    sa = Source.coerce_address("https://example.org/file.R")
    assert sa.type == UrlSource

    # An address that is not matched by any source type
    with pytest.raises(ValueError, match='Unable to parse source address "foo"'):
        sa = Source.coerce_address("foo")


def test_default_parse_address():
    sa = DatSource.parse_address("foo")
    assert sa is None

    sa = DatSource.parse_address("dat://")
    assert sa.type == DatSource


def test_query_from_address():
    q = Source.query_from_address(SourceAddress("Github", repo="org/repo"))
    assert isinstance(q, Q)
    assert q.children == [("GithubSource__repo", "org/repo")]

    q = Source.query_from_address(
        SourceAddress("Github", repo="org/repo", subpath="a/sub/folder")
    )
    assert q.children == [
        ("GithubSource__repo", "org/repo"),
        ("GithubSource__subpath", "a/sub/folder"),
    ]

    q = Source.query_from_address(
        SourceAddress("Github", repo="org/repo"), prefix="sources"
    )
    assert q.children == [("sources__GithubSource__repo", "org/repo")]

    q = Source.query_from_address(
        SourceAddress("Github", repo="org/repo", subpath="a/sub/folder"),
        prefix="sources",
    )
    assert q.children == [
        ("sources__GithubSource__repo", "org/repo"),
        ("sources__GithubSource__subpath", "a/sub/folder"),
    ]


@pytest.mark.django_db
def test_create_from_address():
    s = Source.create_from_address(
        SourceAddress("Github", repo="org/repo", subpath="a/folder")
    )
    assert isinstance(s, GithubSource)
    assert s.repo == "org/repo"
    assert s.subpath == "a/folder"

    s = Source.create_from_address("github://org/repo")
    assert isinstance(s, GithubSource)
    assert s.repo == "org/repo"
    assert s.subpath is None


def test_github_parse_address():
    for url in [
        "github://django/django",
        "http://github.com/django/django",
        "https://github.com/django/django/",
    ]:
        sa = GithubSource.parse_address(url)
        assert sa.type == GithubSource
        assert sa["repo"] == "django/django"
        assert sa["subpath"] is None

    for url in [
        "github://django/django/django/db/models",
        "http://github.com/django/django/tree/master/django/db/models",
        "https://github.com/django/django/tree/master/django/db/models",
    ]:
        sa = GithubSource.parse_address(url)
        assert sa.type == GithubSource
        assert sa["repo"] == "django/django"
        assert sa["subpath"] == "django/db/models"

    for url in [
        "github://django/django/django/db/models/query_utils.py",
        "https://github.com/django/django/blob/master/django/db/models/query_utils.py",
    ]:
        sa = GithubSource.parse_address(url)
        assert sa.type == GithubSource
        assert sa["repo"] == "django/django"
        assert sa["subpath"] == "django/db/models/query_utils.py"


def test_googledocs_parse_address():
    for url in [
        "gdoc://1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA",
        "docs.google.com/document/d/1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA",
        "https://docs.google.com/document/d/1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA/",
        "https://docs.google.com/document/d/1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA/edit",
    ]:
        sa = GoogleDocsSource.parse_address(url)
        assert sa.type == GoogleDocsSource
        assert sa.doc_id == "1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA"

    # Use of naked ids
    assert (
        GoogleDocsSource.parse_address("1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA")
        is None
    )
    assert (
        GoogleDocsSource.parse_address(
            "1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA", naked=True
        ).doc_id
        == "1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA"
    )

    # Use of strict
    assert GoogleDocsSource.parse_address("foo") is None
    with pytest.raises(ValidationError, match="Invalid Google Doc identifier"):
        GoogleDocsSource.parse_address("foo", strict=True)
