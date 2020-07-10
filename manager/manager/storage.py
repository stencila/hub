"""
Functions related to file storage and serving.

The following functions return different types and configurations of
Django `Storage` classes depending on the use and the deployment context.
See https://docs.djangoproject.com/en/3.0/ref/files/storage/

For security reasons, even public files should be served raw
from a different domain (ala googleusercontent.com and githubusercontent.com).
"""

import os
from urllib.parse import urljoin

from django.conf import settings
from django.conf.urls.static import static
from django.core.files.storage import FileSystemStorage, Storage
from storages.backends.gcloud import GoogleCloudStorage


class MediaStorage(GoogleCloudStorage):
    """
    Custom storage for public media files.

    Overrides the `url()` method to avoids a call to GCS to get a signed URL.
    Other ways may exist to do this (e.g. set `GS_DEFAULT_ACL` to `publicRead`).
    But this approach seems to be the most direct, and has less potential to conflict
    with other GCS-based storages, or the permissions policy on the bucket.
    See:
      - https://stackoverflow.com/questions/34247702/configure-django-and-google-cloud-storage
      - https://github.com/jschneier/django-storages/issues/692
    """

    def __init__(self):
        super().__init__(bucket_name="stencila-hub-media")

    def url(self, name: str) -> str:
        """Get the URL of the file."""
        return urljoin("https://storage.googleapis.com/" + self.bucket_name + "/", name)


def media_storage() -> Storage:
    """
    Get the storage backend for public media files e.g. profile images.

    We use "media" as this is the name given to these sorts of files
    in Django. See https://docs.djangoproject.com/en/3.0/topics/files/.
    """
    return (
        FileSystemStorage(
            location=os.path.join(settings.STORAGE_ROOT, "media"),
            base_url="/local/media",
        )
        if settings.STORAGE_ROOT
        else MediaStorage()
    )


def uploads_storage() -> Storage:
    """
    Get the storage backend for private, uploaded files.
    """
    return (
        FileSystemStorage(
            location=os.path.join(settings.STORAGE_ROOT, "uploads"),
            base_url="/local/uploads",
        )
        if settings.STORAGE_ROOT
        else GoogleCloudStorage(bucket_name="stencila-hub-uploads")
    )


class WorkingStorage(Storage):
    """
    A storage class which returns a link to a file in the working directory of a project.

    This storage class returns a link to a file. The URL:

    - is on another domain to avoid serving potentially malicious content with XSS attacks
      from the hub.

    - for private files has a token to restrict access.

    The URL is similar to that which GitHub uses for user content:
       https://raw.githubusercontent.com/org/repo/master/file?token=AAIZKUGCZQQGDQ4BMMUZ6PS7BYUQO

    The files are actually served by the `router` service.
    """

    def url(path: str):
        """Get the URL for a file."""
        return os.path.join("https://stencila.io/", path)


def working_storage() -> WorkingStorage:
    """
    Get the storage backend for project working directories.

    During development, a
    """
    return (
        FileSystemStorage(
            location=os.path.join(settings.STORAGE_ROOT, "working"),
            base_url="/local/working",
        )
        if settings.STORAGE_ROOT
        else WorkingStorage()
    )


def snapshots_storage() -> Storage:
    """
    Get the storage backend for project snapshots.
    """
    return (
        FileSystemStorage(
            location=os.path.join(settings.STORAGE_ROOT, "snapshots"),
            base_url="/local/snapshots",
        )
        if settings.STORAGE_ROOT
        else GoogleCloudStorage(bucket_name="stencila-hub-snapshots")
    )


def serve_local():
    """
    Serve files from local file storage during development.
    """
    return [
        static(storage.base_url, document_root=storage.location)
        for storage in [
            media_storage(),
            uploads_storage(),
            working_storage(),
            snapshots_storage(),
        ]
        if isinstance(storage, FileSystemStorage)
    ]
