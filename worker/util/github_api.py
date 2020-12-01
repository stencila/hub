import os
from typing import Optional

from github import Github
from stencila.schema.types import Person

from .cache import expiring_lru_cache

# Github API credentials
# Used to authenticate with GitHub API as a OAuth App to get higher rate limits
# See https://developer.github.com/v3/#oauth2-keysecret
# Note that using the credentials of a "Github App" may give lower rate limits
# than using a "OAuth App".
GITHUB_API_CREDENTIALS = os.getenv("GITHUB_API_CREDENTIALS")


def github_client(token: Optional[str] = None) -> Github:
    """
    Create a GitHub API client.
    """
    if token:
        # Authenticate as a user
        return Github(token)
    elif GITHUB_API_CREDENTIALS:
        # Authenticate as a OAuth client application
        # No extra permissions, just higher rate limits
        client_id, client_secret = GITHUB_API_CREDENTIALS.split(":")
        return Github(client_id, client_secret)
    else:
        # Unauthenticated access
        return Github()


@expiring_lru_cache(seconds=180)
def github_user_as_person(user) -> Person:
    """
    Convert a GitHub user to a `Person` node.

    Caches the response to avoid unnecessary API requests which
    can easily happen otherwise.
    """
    person = Person(
        name=user.name or user.login, emails=[user.email] if user.email else None
    )
    return person
