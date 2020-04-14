from django.db.models import Q
import pytest

from projects.source_models import Source, SourceAddress, GithubSource, UrlSource


def test_source_address():
    with pytest.raises(KeyError, match='Unknown source type "foo"'):
        SourceAddress("foo")


def test_parse_address():
    # A specific address (ie. starting with type://)
    sa = Source.parse_address("github://org/repo/a/file.md")
    assert sa.type == GithubSource
    assert sa["repo"] == "org/repo"
    assert sa["subpath"] == "a/file.md"

    # A HTTP URL that is matched by a specific source
    sa = Source.parse_address("https://github.com/org/repo")
    assert sa.type == GithubSource

    # A generic URL that caught as a URL source
    sa = Source.parse_address("https://example.org/file.R")
    assert sa.type == UrlSource

    # An address that is not matched by any source type
    with pytest.raises(ValueError, match='Unable to parse source address "foo"'):
        sa = Source.parse_address("foo")


def test_github_parse():
    for url in [
        "github://django/django",
        "http://github.com/django/django",
        "https://github.com/django/django/",
    ]:
        sa = GithubSource.parse_address(url)
        assert sa.type == GithubSource
        assert sa["repo"] == "django/django"
        assert sa["subpath"] == None

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
    assert s.subpath == None
