import typing
import re
from urllib.parse import urlparse, ParseResult

from allauth.socialaccount.models import SocialToken
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.core.validators import URLValidator
from polymorphic.models import PolymorphicModel

from lib.conversion_types import mimetype_from_path
from lib.google_auth import GoogleAuth
from lib.social_auth_token import user_social_token
from jobs.models import Job
from users.models import User


class SourceAddress(dict):
    """
    A specification of the location of a source.

    Used to store the result of parsing a source address string
    (e.g. a URL), create source instances, specify job parameters,
    filter for existing source instances etc.
    """

    def __init__(self, type_name: str, **kwargs):
        super().__init__(**kwargs)
        self.type_name = type_name
        try:
            self.type = globals()["{}Source".format(type_name)]
        except KeyError:
            raise KeyError('Unknown source type "{}"'.format(type_name))

    def __getattr__(self, attr):
        return self[attr]


class Source(PolymorphicModel):

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

        front = (
            "{}__".format(prefix) if prefix else ""
        ) + address.type.__name__.lower()
        kwargs = dict(
            [("{}__{}".format(front, key), value) for key, value in address.items()]
        )
        return models.Q(**kwargs)

    @staticmethod
    def from_address(address_or_string: typing.Union[SourceAddress, str]) -> "Source":
        """
        Create a source instance from a source address.

        Given a source address, creates a new source instance of the
        specified `type` with fields set from the address.
        """
        address = Source.coerce_address(address_or_string)
        return address.type.objects.create(**address)

    def to_address(self) -> SourceAddress:
        """
        Create a source address from a source instance.

        The inverse of `Source.from_address`. Used primarily
        to create a pull job for a source.
        """
        all_fields = [field.name for field in self._meta.fields]
        class_fields = [
            name for name in self.__class__.__dict__.keys() if name in all_fields
        ]
        return SourceAddress(
            self.type_name,
            **dict(
                [
                    (name, value)
                    for name, value in self.__dict__.items()
                    if name in class_fields
                ],
                type=self.type_name,
            ),
        )

    def pull(self, user: User) -> Job:
        """
        Pull the source to the filesystem.

        Creates a `Job` having the `pull` method and a dictionary of `source`
        attributes sufficient to pull it. This may include authentication tokens.
        """
        return Job.objects.create(
            creator=user,
            method="pull",
            params=dict(
                source=self.to_address(), project=self.project.id, path=self.path
            ),
        )

    def push(self) -> Job:
        """
        Push from the filesystem to the source.

        Creates a `Job` having the `push` method and a dictionary of `source`
        attributes sufficient to push it. This may include authentication tokens.
        """
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


class ElifeSource(Source):
    """An article from https://elifesciences.org."""

    article = models.IntegerField(help_text="The article number.")

    version = models.IntegerField(
        null=True,
        blank=True,
        help_text="The article version. If blank, defaults to the latest.",
    )


class PlosSource(Source):
    """An article from https://journals.plos.org."""

    article = models.TextField(help_text="The article doi.")


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

    def push_from_disk(self, content: typing.Union[str, typing.IO]):
        if isinstance(content, str):
            f = ContentFile(content.encode("utf-8"))
        else:
            f = File(content)
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
        return (
            "github://"
            + self.repo
            + ("/{}".format(self.subpath) if self.subpath else "")
        )

    @property
    def url(self):
        url = "https://github.com/{}".format(self.repo)
        if self.subpath:
            url += "/blob/master/{}".format(self.subpath)
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

    def pull(self, user: User) -> Job:
        source_address = self.to_address()

        gauth = GoogleAuth(user_social_token(user, "google"))
        source_address["token"] = gauth.check_and_refresh_token()

        return Job.objects.create(
            creator=user,
            method="pull",
            params=dict(source=source_address, project=self.project.id, path=self.path),
        )


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

        return mimetype_from_path(self.url) or "application/octet-stream"

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = False, strict: bool = False
    ) -> typing.Optional[SourceAddress]:
        url: typing.Optional[str] = address
        try:
            URLValidator()(url)
        except ValidationError:
            url = None

        if url:
            return SourceAddress("Url", url=url)

        if strict:
            raise ValidationError("Invalid URL source: {}".format(address))

        return None


# TODO: this could be a typing.NamedTuple
class LinkedSourceAuthentication(object):
    """Container for token(s) a user has for authenticating to remote sources."""

    github_token: typing.Optional[str]
    google_token: SocialToken  # TODO: Should be optional

    def __init__(
        self,
        github_token: typing.Optional[str] = None,
        google_token: typing.Optional[SocialToken] = None,
    ) -> None:
        self.github_token = github_token
        self.google_token = google_token
