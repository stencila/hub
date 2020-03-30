"""
Functional tests of Hub URLs.

These are pretty much "smoke tests" with the main aim being to catch
severe regressions. Although they serve this purpose quite well, prefer
writing unit tests over relying on these tests, particularly
for test driven development.
"""

from collections import namedtuple
import re
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
import pytest

from accounts.models import Account
from projects.models import Project

# Shorthand functions for creating regexes to match response HTML against


def title(title):
    """Create a regex for the <title> tag."""
    return "<title>{} : Stencila</title>".format(title)


def link(href):
    """Create a regex for a <a> tag."""
    return '<a ([^>]*?)href="{}"'.format(href)


# Shorthand sets of expectations for certain pages

signin = [200, title("Sign in")]

# Define a check
# Each check is for a path and defines the expected
# response for each user
# Expectations can be an integer response code, a
# a string regex pattern, or a list of either of those
Check = namedtuple("Check", "path anon joe mary")


def check(path, anon=None, joe=None, mary=None):
    return Check(path, anon, joe, mary)


# Skip a check
# Change `check` to `skip`
# instead of having to comment out multiple lines
def skip(path, *args, **kwargs):
    print("Skipping {}".format(path))
    return None


# fmt: off
checks = [
    check(
        "/",
        anon=title("Open"),
        joe=title("Dashboard")
    ),
    check(
        "/me",
        anon=signin,
        joe=title("User settings")
    ),
    check(
        "/me/password/change/",
        anon=signin,
        joe=title("Password Change")
    ),
    check(
        "/me/email/",
        anon=signin,
        joe=title("Manage e-mail addresses")
    ),
    check(
        "/me/social/connections/",
        anon=signin,
        joe=title("")
    ),
    check(
        "/me/avatar/change/",
        anon=signin,
        joe=title("")
    ),
    check(
        "/me/username/",
        anon=signin,
        joe=title("Change Username : Stencila")
    ),
    check(
        "/accounts",
        anon=signin,
        joe=[title("Account  : Teams"), link(reverse("account_create"))],
    ),
    check(
        "/joe-personal-account",
        anon=signin,
        joe=title("Account joe-personal-account")
    ),
    check(
        "/joe-personal-account/members",
        anon=signin,
        joe=title("Account joe-personal-account : Members"),
    ),
    check(
        "/joe-personal-account/teams",
        anon=signin,
        joe=title("Account 1 : Teams")
    ),
    check(
        "/joe-personal-account/settings",
        anon=signin,
        joe=title("Account 1 : Settings")
    ),
    check(
        "/joe-personal-account/subscriptions",
        anon=signin,
        joe=title("Account joe-personal-account : Subscriptions"),
    ),
    check(
        "/joe-personal-account/subscriptions/add",
        anon=signin,
        joe="plan"
    ),
    check(
        "/projects",
        anon=title("Projects"),
        joe=[title("Projects"), link(reverse("project_create"))],
    ),
    # Most (all?) of the following tests generate the warning for all(?) users:
    #  warnings.warn("ProjectPermissionsMixin GET", DeprecationWarning)
    check(
        "/joe-personal-account/public-project",
        anon=title("public-project : Overview"),
        joe=title("public-project : Overview"),
        mary=title("public-project : Overview")
    ),
    check(
        "/joe-personal-account/private-project",
        anon=403,
        joe=title("private-project : Overview"),
        mary=403
    ),
    check(
        "/joe-personal-account/private-project/files",
        anon=403,
        joe=title("Project private-project: Files"),
        mary=403
    ),
    check(
        "/joe-personal-account/private-project/snapshots",
        anon=403,
        joe=title("Project private-project: Snapshots"),
        mary=403
    ),
    check(
        "/joe-personal-account/private-project/archives",
        anon=403,
        joe=title("Project 2: Files"),
        mary=403
    ),
    check(
        "/joe-personal-account/private-project/activity",
        anon=403,
        joe=title("Project 2: Activity"),
        mary=403
    ),
    check(
        "/joe-personal-account/private-project/sharing",
        anon=403,
        joe=title("Project 2 : Sharing"),
        mary=403
    ),
    check(
        "/joe-personal-account/private-project/settings/metadata",
        anon=403,
        joe=title("Project 2 : Settings : Metadata"),
        mary=403
    ),
    check(
        "/joe-personal-account/private-project/settings/access",
        anon=403,
        joe=title("Project 2 : Settings : Access"),
        mary=403
    ),
]
# fmt: on


# The following turns warnings into errors to help debug where those
# are being generated.
# For finer grained control see https://docs.pytest.org/en/latest/warnings.html
# pytestmark = pytest.mark.filterwarnings("error")


@pytest.mark.django_db
class Fixture(TestCase):
    """Setup the database as a test fixture."""

    def setUp(self):
        joe = User.objects.create_user(username="joe", password="joe")
        joes_account = Account.objects.get(name="joe-personal-account")
        Project.objects.create(
            account=joes_account, creator=joe, public=True, name="public-project"
        )
        Project.objects.create(
            account=joes_account, creator=joe, public=False, name="private-project"
        )

        User.objects.create_user(username="mary", password="mary")


@pytest.mark.django_db
class AnonTest(Fixture):
    """Test URL response status codes for unauthenticated users."""

    who = "anon"

    def test_urls(self):
        for check in checks:
            if not isinstance(check, Check):
                continue

            expects = getattr(check, self.who)
            if expects is None:
                continue

            response = self.client.get(check.path, follow=True)
            content = response.content.decode("utf-8")
            for expect in expects if isinstance(expects, list) else [expects]:
                if isinstance(expect, int):
                    assert response.status_code == expect
                elif isinstance(expect, str):
                    self.assertIsNotNone(
                        re.search(expect, content),
                        'Could not find regex "{}" in path {}'.format(
                            expect, check.path
                        ),
                    )
                else:
                    raise Exception(
                        "Unhandled expectation type: {}".format(type(expect))
                    )


@pytest.mark.django_db
class JoeTest(AnonTest):
    """Test responses for test user Joe."""

    who = "joe"

    def setUp(self):
        super().setUp()
        self.client.login(username="joe", password="joe")


@pytest.mark.django_db
class MaryTest(AnonTest):
    """Test responses for test user Mary."""

    who = "mary"

    def setUp(self):
        super().setUp()
        self.client.login(username="mary", password="mary")
