"""
Functional tests of Hub URLs.

These are pretty much "smoke tests" with the main aim being to catch
severe regressions. Although they serve this purpose quite well, prefer
writing unit tests over relying on these tests, particularly
for test driven development.
"""
import re
import typing

from manager.testing import DatabaseTestCase

# Shorthand functions for creating regexes to match response HTML against


def title(t):
    """Create a regex for the <title> tag."""
    return "<title>{} : Stencila</title>".format(t)


def link(href):
    """Create a regex for a <a> tag."""
    return '<a ([^>]*?)href="{}"'.format(href)


# Shorthand sets of expectations for certain pages

signin = [200, title("Sign in")]
page403 = [403, title("No, no")]
page404 = [404, title("Uh oh!")]

CheckType = typing.Union[int, str]
CheckTypeList = typing.List[CheckType]


# Define a check
# Each check is for a path and defines the expected
# response for each user
# Expectations can be an integer response code, a
# a string regex pattern, or a list of either of those
class Check(typing.NamedTuple):
    path: str
    anon: typing.Optional[typing.Union[CheckTypeList, CheckType]] = None
    ada: typing.Optional[typing.Union[CheckTypeList, CheckType]] = None
    bob: typing.Optional[typing.Union[CheckTypeList, CheckType]] = None


# Skip a check
# Change `check` to `skip`
# instead of having to comment out multiple lines
def skip(path, *args, **kwargs):
    print("Skipping {}".format(path))
    return None


# fmt: off
checks = [
    Check(
        "/",
        anon=title("Projects"),
        ada=title("ada")
    ),
    # User `me` namespace URLs
    Check(
        "/me/password/change/",
        anon=signin,
        ada=title("Change password")
    ),
    Check(
        "/me/email/",
        anon=signin,
        ada=title("Manage e-mail addresses")
    ),
    Check(
        "/me/social/connections/",
        anon=signin,
        ada=title("Manage account connections")
    ),
    # Stencila namespace URLs
    Check(
        "/stencila/admin",
        anon="Log in | Django site admin",
        ada="Log in | Django site admin"
    ),
    Check(
        "/stencila/test/messages",
        anon=title("Home"),
        ada=title("Home")
    ),
    Check(
        "/stencila/test/403",
        anon=page403,
        ada=page403
    ),
    Check(
        "/stencila/test/404",
        anon=page404,
        ada=page404
    ),
    Check(
        "/stencila/render?template=500.html",
        anon=title("Oops!"),
        ada=title("Oops!")
    ),
    # Project URLs
    # Redirects for integer ids
    Check(
        "/projects/1",
        anon=200,
        ada=200,
        bob=200
    ),
    Check(
        "/projects/2",
        anon=404,
        ada=200,
        bob=404
    ),
    # Redirects for integer ids under accounts
    Check(
        "/ada/1",
        anon=200,
        ada=200,
        bob=200
    ),
    Check(
        "/ada/2",
        anon=404,
        ada=200,
        bob=404
    ),
    # Unredirected URLs
    Check(
        "/ada/public/files",
        anon=200,
        ada=200,
        bob=200
    ),
    Check(
        "/ada/private/files",
        anon=404,
        ada=200,
        bob=404
    ),
    Check(
        "/ada/private/sources",
        anon=404,
        ada=200,
        bob=404
    ),
    Check(
        "/ada/private/sources/new/elife",
        anon=signin,
        ada=200,
        bob=404
    ),
    Check(
        "/ada/private/sources/new/url",
        anon=signin,
        ada=200,
        bob=404
    ),
    Check(
        "/ada/private/sources/upload",
        anon=signin,
        ada=200,
        bob=404
    ),
    Check(
        "/ada/private/snapshots",
        anon=404,
        ada=200,
        bob=404
    ),
    Check(
        "/ada/private/jobs",
        anon=signin,
        ada=200,
        bob=404
    ),
    Check(
        "/ada/private/sharing",
        anon=signin,
        ada=200,
        bob=404
    ),
    Check(
        "/ada/private/settings",
        anon=signin,
        ada=200,
        bob=404
    ),
    # API documentation endpoints
    Check(
        "/api",
        anon=title("API"),
        ada=title("API")
    ),
    Check(
        "/api/schema",
        anon=200,
        ada=200
    ),
]


# fmt: on


# The following turns warnings into errors to help debug where those
# are being generated.
# For finer grained control see https://docs.pytest.org/en/latest/warnings.html
# pytestmark = pytest.mark.filterwarnings("error")


class UrlsMixin:
    """Test URL response status codes."""

    def test_urls(self):
        for check in checks:
            if not isinstance(check, Check):
                continue

            expects = getattr(check, self.username)
            if expects is None:
                continue

            response = self.client.get(check.path, follow=True)
            content = response.content.decode("utf-8")
            for expect in expects if isinstance(expects, list) else [expects]:
                if isinstance(expect, int):
                    assert response.status_code == expect, check.path
                elif isinstance(expect, str):
                    self.assertIsNotNone(
                        re.search(expect, content),
                        'Could not find regex "{}" in content of path "{}". Got:\n\n{}'.format(
                            expect, check.path, content
                        ),
                    )
                else:
                    raise Exception(
                        "Unhandled expectation type: {}".format(type(expect))
                    )


class TestUrlsAnon(DatabaseTestCase, UrlsMixin):
    username = "anon"


class TestUrlsAda(DatabaseTestCase, UrlsMixin):
    username = "ada"

    def setUp(self):
        self.client.login(username="ada", password="ada")


class TestUrlsBob(DatabaseTestCase, UrlsMixin):
    username = "bob"

    def setUp(self):
        self.client.login(username="bob", password="bob")
