import enum
import typing
from io import BytesIO
from urllib.parse import urlparse, ParseResult

from allauth.socialaccount.models import SocialToken
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from polymorphic.models import PolymorphicModel

from lib.conversion_types import mimetype_from_path


class MimeTypeDetectMixin(object):
    path: str
    source: typing.Any

    @property
    def mimetype(self) -> str:
        if (
            hasattr(self, "source")
            and self.source is not None
            and hasattr(self.source, "mimetype")
        ):
            mimetype = self.source.mimetype
            if mimetype and mimetype != "Unknown":
                return mimetype

        return mimetype_from_path(self.path) or "Unknown"


class Source(PolymorphicModel, MimeTypeDetectMixin):
    provider_name = ""

    project = models.ForeignKey(
        "Project",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sources",
    )

    path = models.TextField(
        null=False,
        default=".",
        help_text="The path that the file or directory from the source is mapped to in the Project",
    )

    updated = models.DateTimeField(
        auto_now=True, help_text="Time this model instance was last updated"
    )

    def __str__(self) -> str:
        """
        Get a human readable string representation of the source instance.

        These are intended to be URL-like human-readable and -writable
        representations of sources(e.g. `github:org/repo/sub/path`; `gdoc:378yfh2yg362...`).
        They are used in admin lists and API endpoints to allowing quick
        specification of a source (e.g. for filtering).
        """
        raise NotImplementedError(
            "Method `__str__` should be implemented for class {}".format(
                self.__class__.__name__
            )
        )

    @property
    def type(self) -> typing.Type["Source"]:
        """Get the type of a source instance e.g. `GoogleDocsSource`."""
        return ContentType.objects.get_for_id(self.polymorphic_ctype_id).model

    @property
    def type_name(self) -> str:
        """
        Get the name of the type of a source instance.

        The `type_name` is intended for use in user interfaces.
        This base implementation simply drops `Source` from the end
        of the name. Can be overridden in derived classes if
        necessary.
        """
        return self.__class__.__name__[:-6]

    def pull(self) -> BytesIO:
        raise NotImplementedError(
            "Pull is not implemented for class {}".format(self.__class__.__name__)
        )

    def push(self, archive: typing.Union[str, typing.IO]) -> None:
        raise NotImplementedError(
            "Push is not implemented for class {}".format(self.__class__.__name__)
        )

    def save(self, *args, **kwargs):
        # Make sure there are no leading or trailing slashes in the path to make them consistent
        self.path = self.path.strip("/")
        super().save(*args, **kwargs)


# Source classes in alphabetical order
#
# Note: many of these are, obviously, not implemented, but have
# been added here as placeholders, to sketch out the different types of
# project sources that might be available
#
# Note: where these derived classes do not need any additional
# fields you can use `class Meta: abstract = True`
# so that an additional database table is not created.
# However, that means that they are not available in the admin.


class BitbucketSource(Source):
    """A project hosted on Bitbucket."""

    provider_name = "BitBucket"

    class Meta:
        abstract = True


class DatSource(Source):
    """A project hosted on Dat."""

    provider_name = "Dat"

    class Meta:
        abstract = True


class DiskSource(object):
    """Not a Source that is stored in the database but used in directory listing for files that are already on disk."""

    type = "disk"


class DropboxSource(Source):
    """A project hosted on Dropbox."""

    provider_name = "Drop Box"

    class Meta:
        abstract = True


def files_source_file_path(instance: "FileSource", filename: str):
    # File will be uploaded to MEDIA_ROOT/files_projects/<id>/<filename>
    return "projects/{0}/{1}".format(instance.id, filename)


class FileSource(Source):
    """A file uploaded to the Hub."""

    provider_name = "File"

    size = models.IntegerField(
        null=True, blank=True, help_text="Size of the file in bytes"
    )

    file = models.FileField(
        null=False,
        blank=True,
        upload_to=files_source_file_path,
        help_text="The actual file stored",
    )

    def save(self, *args, **kwargs):
        """Override of base superclass `save` method to update the size property from the file size."""
        if self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)

    def pull(self):
        """Pull the file content."""
        if self.file:
            with self.file.open() as file:
                return file.read().decode()
        else:
            return ""

    def pull_binary(self) -> typing.Optional[bytearray]:
        if self.file:
            return self.file.open("rb").read()
        return None

    def push(self, archive: typing.Union[str, typing.IO]):
        if isinstance(archive, str):
            f = ContentFile(archive.encode("utf-8"))
        else:
            f = File(archive)
        self.file.save(self.path, f)
        self.size = self.file.size


class GithubSource(Source):
    """A project hosted on Github."""

    provider_name = "GitHub"

    repo = models.TextField(
        null=False,
        blank=False,
        help_text="The Github repository identifier i.e. org/repo",
    )

    subpath = models.TextField(
        null=True, blank=True, help_text="Path to file or folder within the repository"
    )

    def __str__(self) -> str:
        return "{}/{}".format(self.repo, self.subpath or "")


class GitlabSource(Source):
    """A project hosted on Gitlab."""

    provider_name = "GitLab"

    class Meta:
        abstract = True


class GoogleDocsSource(Source):
    """A reference to a Google Docs document."""

    provider_name = "GoogleDocs"

    doc_id = models.TextField(null=False, help_text="Google's ID of the document.")

    @property
    def mimetype(self) -> str:
        return "application/vnd.google-apps.document"


class OSFSource(Source):
    """
    A project hosted on the Open Science Framework.

    See https://developer.osf.io/ for API documentation.
    """

    provider_name = "OSF"

    class Meta:
        abstract = True


class UrlSource(Source):
    """A source that is downloaded from a URL on demand."""

    provider_name = "URL"

    url = models.URLField(help_text="The URL of the remote file.")

    _url_obj: typing.Optional[ParseResult] = None

    def __str__(self) -> str:
        return self.url

    def _parse_url(self) -> ParseResult:
        if self._url_obj is None:
            self._url_obj = urlparse(self.url)
        return self._url_obj

    @property
    def hostname_lower(self) -> typing.Optional[str]:
        hostname = self._parse_url().hostname
        return hostname.lower() if hostname else None

    @property
    def is_elife_url(self) -> bool:
        return self.hostname_lower == "elifesciences.org"

    @property
    def is_plos_url(self) -> bool:
        return self.hostname_lower == "journals.plos.org"

    @property
    def mimetype(self) -> str:
        if self.is_elife_url or self.is_plos_url:
            return "text/html"

        return super(UrlSource, self).mimetype


class LinkedSourceAuthentication(object):
    """Container for token(s) a user has for authenticating to remote sources."""

    github_token: typing.Optional[str]
    google_token: SocialToken

    def __init__(
        self,
        github_token: typing.Optional[str] = None,
        google_token: typing.Optional[SocialToken] = None,
    ) -> None:
        self.github_token = github_token
        self.google_token = google_token
