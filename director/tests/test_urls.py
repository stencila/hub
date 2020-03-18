"""
Functional tests of Hub URLs

These are pretty much "smoke tests" with the main aim being to catch
severe regressions. Although they serve their purpose, prefer
unit tests over these.
"""
from collections import namedtuple
import re
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
import pytest

from accounts.models import Account
from projects.models import Project

# Shorthand functions fro creating regexes to match response HTML against


def title(title):
    """Create a regex for the <title> tag"""
    return f"<title>{title} : Stencila</title>"


def link(href):
    """Create a regex for a link (<a>) tag"""
    return f'<a (.+?)?href="{href}"'


# Shorthand sets of expectations for certain pages

signin = [200, title("Sign in")]

# Each test is for a path and defines the expected
# response for each test user
test = namedtuple("Test", "path anon joe")
tests = [
    test("/", signin, title("Dashboard")),
    test("/me", signin, title("User settings")),
    test("/me/password/change/", signin, title("Password Change")),
    test("/me/email/", signin, title("Manage e-mail addresses")),
    test("/me/social/connections/", signin, title("")),
    test("/me/avatar/change/", signin, title("")),
    test("/me/username/", signin, title("Change Username : Stencila")),
    test(
        "/accounts",
        signin,
        [title("Account  : Teams"), link(reverse("account_create"))],
    ),
    test("/joe-personal-account", signin, title("Account joe-personal-account")),
    test(
        "/joe-personal-account/members",
        signin,
        title("Account joe-personal-account : Members"),
    ),
    test("/joe-personal-account/teams", signin, title("Account 1 : Teams")),
    test("/joe-personal-account/settings", signin, title("Account 1 : Settings")),
    test(
        "/joe-personal-account/subscriptions",
        signin,
        title("Account joe-personal-account : Subscriptions"),
    ),
    test("/joe-personal-account/subscriptions/add", signin, "plan"),
    test(
        "/projects",
        title("Projects"),
        [title("Projects"), link(reverse("project_create"))],
    ),
    test(
        "/joe-personal-account/public-project",
        title("public-project : Overview"),
        title("public-project : Overview"),
    ),
    test(
        "/joe-personal-account/private-project",
        403,
        title("private-project : Overview"),
    ),
    test(
        "/joe-personal-account/private-project/files",
        403,
        title("Project private-project: Files"),
    ),
    test(
        "/joe-personal-account/private-project/snapshots",
        403,
        title("Project private-project: Snapshots"),
    ),
    test(
        "/joe-personal-account/private-project/archives",
        403,
        title("Project 2: Files"),
    ),
    test(
        "/joe-personal-account/private-project/activity",
        403,
        title("Project 2: Activity"),
    ),
    test(
        "/joe-personal-account/private-project/sharing",
        403,
        title("Project 2 : Sharing"),
    ),
    test(
        "/joe-personal-account/private-project/settings/metadata",
        403,
        title("Project 2 : Settings : Metadata"),
    ),
    test(
        "/joe-personal-account/private-project/settings/access",
        403,
        title("Project 2 : Settings : Access"),
    ),
]


@pytest.mark.django_db
class Fixture(TestCase):
    """Setup the database as a test fixture"""

    def setUp(self):
        joe = User.objects.create_user(username="joe", password="joe")
        joes_account = Account.objects.get(name="joe-personal-account")
        Project.objects.create(
            account=joes_account, creator=joe, public=True, name="public-project"
        )
        Project.objects.create(
            account=joes_account, creator=joe, public=False, name="private-project"
        )


@pytest.mark.django_db
class AnonTest(Fixture):
    """Test URL response status codes for unauthenticated users"""

    who = "anon"

    def test_urls(self):
        for test in tests:
            response = self.client.get(test.path, follow=True)
            content = response.content.decode("utf-8")
            expects = getattr(test, self.who)
            for expect in expects if isinstance(expects, list) else [expects]:
                if isinstance(expect, int):
                    assert response.status_code == expect
                elif isinstance(expect, str):
                    self.assertIsNotNone(
                        re.search(expect, content),
                        f'Could not find regex "{expect}" in path {test.path}',
                    )
                else:
                    raise Exception(
                        "Unhandled expectation type: {}".format(type(expect))
                    )


@pytest.mark.django_db
class JoeTest(AnonTest):
    """Test response status codes for test user Joe"""

    who = "joe"

    def setUp(self):
        super().setUp()
        self.client.login(username="joe", password="joe")
