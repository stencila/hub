import json
import os
from typing import Dict

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials


def google_credentials(secrets: Dict) -> GoogleCredentials:
    """
    Create a Google credentials object to use with Google APIs.
    """
    assert secrets.get(
        "access_token"
    ), """A Google access token is required. Please connect a Google account to your Stencila
 account at https://hub.stenci.la/me/social/connections/."""

    return GoogleCredentials(
        access_token=secrets.get("access_token"),
        client_id=secrets.get("client_id"),
        client_secret=secrets.get("client_secret"),
        refresh_token=secrets.get("refresh_token"),
        token_expiry=None,
        token_uri="https://accounts.google.com/o/oauth2/token",
        user_agent="Stencila Hub Client",
    )


def gdocs_service(secrets: Dict):
    """
    Build a Google Docs API service client.
    """
    return build(
        "docs", "v1", credentials=google_credentials(secrets), cache_discovery=False
    )


def gdrive_service(secrets: Dict):
    """
    Build a Google Drive API service client.
    """
    return build(
        "drive", "v3", credentials=google_credentials(secrets), cache_discovery=False
    )
