"""
Functions related to file storage and serving.

The following functions return different types and configurations of
Django `Storage` classes depending on the use and the deployment context.
See https://docs.djangoproject.com/en/3.0/ref/files/storage/

For security reasons, even public files should be served raw
from a different domain (ala googleusercontent.com and githubusercontent.com).
"""

from typing import Optional
from urllib.parse import urljoin

import httpx
from django.conf import settings
from django.conf.urls.static import static
from django.core.files.storage import FileSystemStorage as BaseFileSystemStorage
from django.core.files.storage import Storage
from django.http import FileResponse, HttpResponse
from storages.backends.gcloud import GoogleCloudStorage as BaseGoogleCloudStorage

http = httpx.Client()


class FileSystemStorage(BaseFileSystemStorage):
    """
    A custom filesystem storage.

    Implements the `response()` and `read()` methods.
    This is done to have a consistent interface between local and remote files
    for reading their content.
    """

    def response(self, path: str) -> HttpResponse:
        """
        Create a HTTP response to a request to download a file.
        """
        file = self.open(path)
        return FileResponse(file)

    def read(self, path: str) -> bytes:
        """
        Read the contents of the file.
        """
        with self.open(path) as file:
            return file.read()


class GoogleCloudStorage(BaseGoogleCloudStorage):
    """
    A custom storage for Google Cloud buckets.
    """

    def response(self, path: str, limit_rate: Optional[str] = "off") -> HttpResponse:
        """
        Create a HTTP response to a request to download a file.

        Send the `X-Accel-Redirect` and other headers
        so that Nginx will reverse proxy the file from the bucket.
        """
        response = HttpResponse()
        response["X-Accel-Redirect"] = "@account-content"
        response["X-Accel-Redirect-URL"] = self.url(path)
        response["X-Accel-Limit-Rate"] = limit_rate
        return response

    def read(self, path: str) -> bytes:
        """
        Read the contents of the file.
        """
        url = self.url(path)
        for attempt in range(5):
            response = http.get(url)
            if response.status_code == 200:
                return response.content
        raise RuntimeError("Unable to fetch file from Google Cloud Storage")


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
        FileSystemStorage(location=settings.MEDIA_ROOT, base_url="/local/media",)
        if settings.MEDIA_ROOT
        else MediaStorage()
    )


def uploads_storage() -> Storage:
    """
    Get the storage backend for private, uploaded files.
    """
    return (
        FileSystemStorage(location=settings.UPLOADS_ROOT, base_url="/local/uploads",)
        if settings.UPLOADS_ROOT
        else GoogleCloudStorage(bucket_name="stencila-hub-uploads")
    )


def working_storage() -> Storage:
    """
    Get the storage backend for project working directories.
    """
    return FileSystemStorage(location=settings.WORKING_ROOT, base_url="/local/working",)


def snapshots_storage() -> Storage:
    """
    Get the storage backend for project snapshots.
    """
    return (
        FileSystemStorage(
            location=settings.SNAPSHOTS_ROOT, base_url="/local/snapshots",
        )
        if settings.SNAPSHOTS_ROOT
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


class StorageUsageMixin:
    """
    A mixin for models that make use of storage providers.

    Classes using this mixin should define `STORAGE` as an
    instance of one of the above classes and override
    `file_location` if necessary.
    """

    STORAGE: Storage

    def file_location(self, file: str) -> str:
        """
        Get the location of one of the models's files relative to the root of the storage volume.
        """
        return file

    def file_url(self, file: str) -> str:
        """
        Get the storage URL of one of the model's files.
        """
        return self.STORAGE.url(self.file_location(file))

    def file_response(self, file: str) -> bytes:
        """
        Create a HTTP response to a request to download one of the model's files.
        """
        return self.STORAGE.response(self.file_location(file))

    def file_content(self, file: str) -> bytes:
        """
        Get the content of one of the model's files.
        """
        return self.STORAGE.read(self.file_location(file))
