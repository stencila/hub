import os
from typing import Optional

from github import Github

# Github API credentials
# Used to authenticate with GitHub API as a OAuth App to get higher rate limits
# See https://developer.github.com/v3/#oauth2-keysecret
# Note that using the credentials of a "Github App" may give lower rate limits
# than using a "OAuth App".
GITHUB_API_CREDENTIALS = os.getenv("GITHUB_API_CREDENTIALS")


def github_client(self, token: Optional[str] = None) -> Github:
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
