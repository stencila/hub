import typing
from io import BytesIO
import re
from urllib.parse import urlparse, ParseResult

from allauth.socialaccount.models import SocialToken
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from polymorphic.models import PolymorphicModel

from lib.conversion_types import mimetype_from_path
from users.models import User


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


class SourceAddress(dict):
    """
    A specification of the location of a source.

    Used to store the result of parsing a source address string
    (e.g. a URL) and use it to create source instances, filter for
    existing source instances etc.
    """

    def __init__(self, type, **kwargs):
        super().__init__(**kwargs)
        try:
            self.type = globals()["{}Source".format(type)]
        except KeyError:
            raise KeyError('Unknown source type "{}"'.format(type))

    def __getattr__(self, attr):
        return self[attr]


class Source(PolymorphicModel, MimeTypeDetectMixin):

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

    creator = models.ForeignKey(
        User,
        null=True,  # Should only be null if the creator is deleted
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sources_created",
        help_text="The user who created the source.",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="The time the source was created."
    )

    updated = models.DateTimeField(
        auto_now=True, help_text="The time the source was last changed"
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

    def __str__(self) -> str:
        """
        Get a human readable string representation of the source instance.

        These are intended to be URL-like human-readable and -writable shorthand
        representations of sources (e.g. `github://org/repo/sub/path`; `gdoc://378yfh2yg362...`).
        They are used in admin lists and in API endpoints to allowing quick
        specification of a source (e.g. for filtering).
        Should be parsable by the `parse_address` method of each subclass.

        In addition, subclasses should implement a `url` property
        that returns a valid URL that is a "backlink" to the source.
        """
        return "{}://{}".format(self.type_name.lower(), self.id)

    @property
    def provider_name(self) -> str:
        """
        Get the name of the provider of a source instance.

        Intended mainly for user interfaces (e.g. to send a message to a client
        that they need to authenticate with a provider in order to
        use a particular source type). Will usually be the same as the `type_name`,
        but derived classes can override if not.
        """
        return self.type_name

    @staticmethod
    def coerce_address(address: typing.Union[SourceAddress, str]) -> SourceAddress:
        """
        Coerce a string into a `SourceAddress`.

        If the `address` is already an instance of `SourceAddress` it
        will be returned unchanged. Otherwise, the `parse_address`
        method of each source type (ie. subclass of `Source`) will
        be called. The first class that returns a `SourceAddress` wins.
        """
        if isinstance(address, SourceAddress):
            return address

        for cls in Source.__subclasses__():
            result = cls.parse_address(address)
            if result is not None:
                return result

        raise ValueError('Unable to parse source address "{}"'.format(address))

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = False, strict: bool = False
    ) -> typing.Optional[SourceAddress]:
        """
        Parse a string into a `SourceAddress`.

        This default implementation just matches the default string
        representation of a source, as generated by `Source.__str__`.
        Derived classes should override this method to match their own
        `__str__` method.
        """
        type_name = cls.__name__[:-6]
        if address.startswith(type_name.lower() + "://"):
            return SourceAddress(type_name)

        if strict:
            raise ValidationError("Invalid source identifier: {}".format(address))

        return None

    @staticmethod
    def query_from_address(
        address_or_string: typing.Union[SourceAddress, str],
        prefix: typing.Optional[str] = None,
    ) -> models.Q:
        """
        Create a query object for a source address.

        Given a source address, constructs a Django `Q` object which
        can be used in ORM queries. Use the `prefix` argument
        when you want to use this function for a related field. For example,

            Source.query_from_address({
                "type": "Github",
                "repo": "org/repo",
                "subpath": "folder"
            }, prefix="sources")

        is equivalent to :

            Q(
                sources__githubsource__repo="org/repo",
                sources__githubsource__subpath="folder"
            )
        """
        address = Source.coerce_address(address_or_string)

        front = ("{}__".format(prefix) if prefix else "") + address.type.__name__.lower()
        kwargs = dict(
            [("{}__{}".format(front, key), value) for key, value in address.items()]
        )
        return models.Q(**kwargs)

    @staticmethod
    def create_from_address(
        address_or_string: typing.Union[SourceAddress, str]
    ) -> "Source":
        """
        Create a source instance from a source address.

        Given a source address, creates a new source instance of the
        specified `type` with fields set from the address.
        """
        address = Source.coerce_address(address_or_string)
        return address.type.objects.create(**address)

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

    class Meta:
        abstract = True


class DatSource(Source):
    """A project hosted on Dat."""

    class Meta:
        abstract = True


class DiskSource(object):
    """Not a Source that is stored in the database but used in directory listing for files that are already on disk."""

    type = "disk"


class DropboxSource(Source):
    """A project hosted on Dropbox."""

    class Meta:
        abstract = True


def files_source_file_path(instance: "FileSource", filename: str):
    # File will be uploaded to MEDIA_ROOT/files_projects/<id>/<filename>
    return "projects/{0}/{1}".format(instance.id, filename)


class FileSource(Source):
    """A file uploaded to the Hub."""

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

    def __str__(self) -> str:
        return "file://{}".format(self.file.name or "")


class GithubSource(Source):
    """A project hosted on Github."""

    repo = models.TextField(
        null=False,
        blank=False,
        help_text="The Github repository identifier i.e. org/repo",
    )

    subpath = models.TextField(
        null=True, blank=True, help_text="Path to file or folder within the repository"
    )

    def __str__(self) -> str:
        return "github://{}/{}".format(self.repo, self.subpath or "")

    @property
    def url(self):
        url = "https://github.com/{}/".format(self.repo)
        if self.subpath:
            url += "blob/master/{}".format(self.subpath)
        return url

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = False, strict: bool = False
    ) -> typing.Optional[SourceAddress]:
        match = re.search(
            r"^github://((?:[a-z0-9\-]+)/(?:[a-z0-9\-_]+))/?(.+)?$", address, re.I
        )
        if match:
            return SourceAddress("Github", repo=match.group(1), subpath=match.group(2))

        match = re.search(
            r"^(?:https?://)?github\.com/((?:[a-z0-9\-]+)/(?:[a-z0-9\-_]+))/?(?:(?:tree|blob)/(?:[^/]+)/(.+))?$",
            address,
            re.I,
        )
        if match:
            return SourceAddress("Github", repo=match.group(1), subpath=match.group(2))

        if strict:
            raise ValidationError(
                "Invalid Github source identifier: {}".format(address)
            )

        return None


class GitlabSource(Source):
    """A project hosted on Gitlab."""

    class Meta:
        abstract = True


class GoogleDocsSource(Source):
    """A reference to a Google Docs document."""

    doc_id = models.TextField(null=False, help_text="Google's ID of the document.")

    @property
    def provider_name(self) -> str:
        return "Google"

    @property
    def mimetype(self) -> str:
        return "application/vnd.google-apps.document"

    def __str__(self) -> str:
        return "gdoc://{}".format(self.doc_id)

    @property
    def url(self) -> str:
        return "https://docs.google.com/document/d/{}/edit".format(self.doc_id)

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = False, strict: bool = False
    ) -> typing.Optional[SourceAddress]:
        doc_id = None

        match = re.search(r"^gdoc://(.+)$", address, re.I)
        if match:
            doc_id = match.group(1)

        match = re.search(
            r"^(?:https://)?docs.google.com/document/d/([^/]+)/?.*", address, re.I
        )
        if match:
            doc_id = match.group(1)

        # No match so far, maybe a naked doc id was supplied
        if naked and not doc_id:
            doc_id = address

        # Check it's a valid id
        if doc_id:
            doc_id = (
                doc_id
                if re.search(r"^([a-z\d])([a-z\d_\-]+)$", doc_id, re.I)
                else doc_id
            )

        if doc_id:
            return SourceAddress("GoogleDocs", doc_id=doc_id)

        if strict:
            raise ValidationError("Invalid Google Doc identifier: {}".format(address))

        return None


class OSFSource(Source):
    """
    A project hosted on the Open Science Framework.

    See https://developer.osf.io/ for API documentation.
    """

    class Meta:
        abstract = True


class UrlSource(Source):
    """A source that is downloaded from a URL on demand."""

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

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = False, strict: bool = False
    ) -> typing.Optional[SourceAddress]:
        match = re.search(r"^https?://", address, re.I)
        if match:
            return SourceAddress("Url", url=address)

        if strict:
            raise ValidationError("Invalid URL source: {}".format(address))

        return None


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
