"""
Functions related to "media" storage and serving.

Here, "media" is used in the Django sense of the word
- user uploaded, or generated, content (e.g. published
HTML, account images) in contrast to "static"
content (e.g. CSS and JS files).

We have two buckets for those files - one that is public and which
can be served via a CDN and one which is private and needs
authorization to access particular files.

For security reasons, the public media files are best served
from a different domain (ala googleusercontent.com and githubusercontent.com)
"""

import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.gcloud import GoogleCloudStorage


def public_storage():
    """
    Get the storage backend for public files.

    In production, a publically accessible bucket.
    In development, a local filesystem directory.
    """
    return (
        GoogleCloudStorage(bucket_name="stencila-hub-public")
        if settings.STORAGE_MODE == "bucket"
        else FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "public"))
    )


def private_storage():
    """
    Get the storage backend for private files.

    In production, a bucket that requires a token to access files.
    In development, a local filesystem directory.
    """
    return (
        GoogleCloudStorage(bucket_name="stencila-hub-private")
        if settings.STORAGE_MODE == "bucket"
        else FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "private"))
    )
