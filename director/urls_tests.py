"""
Functional tests of Hub URLs.

These are pretty much "smoke tests" with the main aim being to catch
severe regressions. Although they serve this purpose quite well, prefer
writing unit tests over relying on these tests, particularly
for test driven development.
"""
import typing
import re
from django.urls import reverse

from general.testing import AnonTestCase, AdaTestCase, BobTestCase


# Shorthand functions for creating regexes to match response HTML against


def title(t):
    """Create a regex for the <title> tag."""
    return "<title>{} : Stencila</title>".format(t)


def link(href):
    """Create a regex for a <a> tag."""
    return '<a ([^>]*?)href="{}"'.format(href)


# Shorthand sets of expectations for certain pages

signin = [200, title("Sign in")]

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
        anon=title("Open"),
        ada=title("Dashboard")
    ),
    Check(
        "/me",
        anon=signin,
        ada=title("User settings")
    ),
    Check(
        "/me/dashboard",
        anon=signin,
        ada=title("Dashboard")
    ),
    Check(
        "/me/password/change/",
        anon=signin,
        ada=title("Password Change")
    ),
    Check(
        "/me/email/",
        anon=signin,
        ada=title("Manage e-mail addresses")
    ),
    Check(
        "/me/social/connections/",
        anon=signin,
        ada=title("")
    ),
    Check(
        "/me/avatar/change/",
        anon=signin,
        ada=title("")
    ),
    Check(
        "/me/username/",
        anon=signin,
        ada=title("Change Username : Stencila")
    ),
    Check(
        "/orgs/",
        anon=signin,
        ada=[title("Organisation : Teams"), link(reverse("account_create"))],
    ),
    Check(
        "/ada",
        anon=signin,
        ada=title("Organisation ada")
    ),
    Check(
        "/ada/settings",
        anon=signin,
        ada=title("Organisation ada : Settings")
    ),
    Check(
        "/ada/subscriptions",
        anon=signin,
        ada=title("Organisation ada : Subscriptions"),
    ),
    Check(
        "/ada/subscriptions/add",
        anon=signin,
        ada="plan"
    ),
    Check(
        "/projects",
        anon=title("Projects"),
        ada=[title("Projects"), link(reverse("project_create"))],
    ),
    Check(
        "/ada/ada-public-project",
        # Default view is files
        anon=title("Project ada-public-project : Files"),
        ada=title("Project ada-public-project : Files"),
        bob=title("Project ada-public-project : Files")
    ),
    Check(
        "/ada/ada-private-project",
        anon=403,
        # Default view is files
        ada=title("Project ada-private-project : Files"),
        bob=403
    ),
    Check(
        "/ada/ada-private-project/files",
        anon=403,
        ada=title("Project ada-private-project : Files"),
        bob=403
    ),
    Check(
        "/ada/ada-private-project/snapshots",
        anon=403,
        ada=title("Project ada-private-project : Snapshots"),
        bob=403
    ),
    Check(
        "/ada/ada-private-project/jobs",
        anon=403,
        ada=title("Project ada-private-project : Jobs"),
        bob=403
    ),
    Check(
        "/ada/ada-private-project/sharing",
        anon=403,
        ada=title("Project ada-private-project : Sharing"),
        bob=403
    ),
    Check(
        "/ada/ada-private-project/settings",
        anon=403,
        ada=title("Project ada-private-project : Settings"),
        bob=403
    ),
    # API endpoints
    Check(
        "/api",
        anon=title("Stencila Hub API"),
        ada=title("Stencila Hub API")
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
                        'Could not find regex "{}" in content of "{}"'.format(
                            expect, check.path
                        ),
                    )
                else:
                    raise Exception(
                        "Unhandled expectation type: {}".format(type(expect))
                    )


class TestUrlsAnon(AnonTestCase, UrlsMixin):
    username = "anon"


class TestUrlsAda(AdaTestCase, UrlsMixin):
    username = "ada"


class TestUrlsBob(BobTestCase, UrlsMixin):
    username = "bob"
