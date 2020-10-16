import datetime
import os
import re
from enum import Enum, unique
from typing import Dict, List, Optional, Type, Union

from allauth.socialaccount.models import SocialApp
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import URLValidator
from django.db import models, transaction
from django.utils import timezone
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel

from jobs.models import Job, JobMethod
from manager.helpers import EnumChoice
from manager.storage import uploads_storage
from projects.models.projects import Project
from users.models import User
from users.socialaccount.tokens import Provider, get_user_social_token


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


def NON_POLYMORPHIC_CASCADE(collector, field, sub_objs, using):
    """
    Cascade delete polymorphic models.

    Without this, a `django.db.utils.IntegrityError: FOREIGN KEY constraint failed` error
    occurs when deleting a project with more than one type of source.
    See https://github.com/django-polymorphic/django-polymorphic/issues/229#issuecomment-398434412
    """
    return models.CASCADE(collector, field, sub_objs.non_polymorphic(), using)


class Source(PolymorphicModel):
    """
    A project source.
    """

    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=NON_POLYMORPHIC_CASCADE,
        related_name="sources",
    )

    address = models.TextField(
        null=False,
        blank=False,
        help_text="The address of the source. e.g. github://org/repo/subpath",
    )

    path = models.TextField(
        null=False,
        blank=False,
        help_text="The path that the source is mapped to in the project.",
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
        auto_now=True, help_text="The time the source was last changed."
    )

    jobs = models.ManyToManyField(
        Job,
        help_text="Jobs associated with this source. "
        "e.g. pull, push or convert jobs",
    )

    # The default object manager which will fetch data from multiple
    # tables (one query for each type of source)
    objects = PolymorphicManager()

    # An additional manager which will only fetch data from the `Source`
    # table.
    objects_base = models.Manager()

    class Meta:
        constraints = [
            # Constraint to ensure that sources are not duplicated within a
            # project. Note that sources can share the same `path` e.g.
            # two sources both targetting a `data` folder.
            models.UniqueConstraint(
                fields=["project", "address"], name="%(class)s_unique_project_address"
            )
        ]

    def __str__(self) -> str:
        return self.address

    @property
    def type_class(self) -> str:
        """
        Get the name the class of a source instance.

        If this is an instance of a derived class then returns that class name.
        Otherwise, fetches the name of the model class based on the `polymorphic_ctype_id`
        (with caching) and then cases it properly.
        """
        if self.__class__.__name__ != "Source":
            return self.__class__.__name__

        all_lower = ContentType.objects.get_for_id(self.polymorphic_ctype_id).model
        for cls in Source.__subclasses__():
            if cls.__name__.lower() == all_lower:
                return cls.__name__
        return ""

    @property
    def type_name(self) -> str:
        """
        Get the name of the type of a source instance.

        The `type_name` is intended for use in user interfaces.
        This base implementation simply drops `Source` from the end
        of the name. Can be overridden in derived classes if
        necessary.
        """
        return self.type_class[:-6]

    @staticmethod
    def class_from_type_name(type_name: str) -> Type["Source"]:
        """Find the class matching the type name."""
        for cls in Source.__subclasses__():
            if cls.__name__.lower().startswith(type_name.lower()):
                return cls

        raise ValueError('Unable to find class matching "{}"'.format(type_name))

    def make_address(self) -> str:
        """
        Create a human readable string representation of the source instance.

        These are intended to be URL-like human-readable and -writable shorthand
        representations of sources (e.g. `github://org/repo/sub/path`; `gdoc://378yfh2yg362...`).
        They are used in admin lists and in API endpoints to allowing quick
        specification of a source (e.g. for filtering).
        Should be parsable by the `parse_address` method of each subclass.
        """
        return "{}://{}".format(self.type_name.lower(), self.id)

    @staticmethod
    def coerce_address(address: Union[SourceAddress, str]) -> SourceAddress:
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
    ) -> Optional[SourceAddress]:
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
        address_or_string: Union[SourceAddress, str], prefix: Optional[str] = None,
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
    def from_address(address_or_string: Union[SourceAddress, str], **other) -> "Source":
        """
        Create a source instance from a source address.

        Given a source address, creates a new source instance of the
        specified `type` with fields set from the address. The `other`
        parameter can be used to set additional fields on the created source.
        """
        address = Source.coerce_address(address_or_string)
        return address.type.objects.create(**address, **other)

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

    def get_secrets(self, user: User) -> Dict:
        """
        Get any secrets required to pull or push the source.

        This method should be overridden by derived classes to return
        a secrets (e.g. OAuth tokens, API keys) specific to the source
        (if necessary).
        """
        return {}

    def get_url(self, path: Optional[str] = None):
        """
        Create a URL for users to visit the source on the external site.

        path: An optional path to a file within the source (for multi-file
              sources such as GitHub repos).
        """
        raise NotImplementedError

    def pull(self, user: Optional[User] = None) -> Job:
        """
        Pull the source to the filesystem.

        Creates a job, and adds it to the source's `jobs` list.
        """
        source = self.to_address()
        secrets = self.get_secrets(user)

        description = "Pull {0}"
        if self.type_class == "UploadSource":
            description = "Collect {0}"
        description = description.format(self.address)

        job = Job.objects.create(
            project=self.project,
            creator=user or self.creator,
            description=description,
            method=JobMethod.pull.value,
            params=dict(
                project=self.project.id, source=source, path=self.path, secrets=secrets
            ),
            **Job.create_callback(self, "pull_callback"),
        )
        self.jobs.add(job)
        return job

    @transaction.atomic
    def pull_callback(self, job: Job):
        """
        Update the files associated with this source.
        """
        result = job.result
        if not result:
            return

        from projects.models.files import File

        # Any existing files for the source, not is results, need to be made
        # non-current
        File.objects.filter(project=self.project, source=self).exclude(
            path__in=result.keys()
        ).update(current=False, updated=timezone.now())

        # Files in in results need to be "created" (i.e. added or have their info updated)
        for path, info in result.items():
            File.create(self.project, path, info, job=job, source=self)

    def push(self) -> Job:
        """
        Push from the filesystem to the source.

        Creates a `Job` having the `push` method and a dictionary of `source`
        attributes sufficient to push it. This may include authentication tokens.
        """
        raise NotImplementedError(
            "Push is not implemented for class {}".format(self.__class__.__name__)
        )

    def preview(self, user: User) -> Job:
        """
        Generate a HTML preview of a source.

        Creates a `series` job comprising a
        `pull` job followed by a `convert` job.
        """
        preview = Job.objects.create(
            project=self.project, creator=user, method="series"
        )
        preview.children.add(self.pull(user))
        preview.children.add(self.convert(user, to="html"))
        return preview

    # Properties related to jobs. Provide shortcuts for
    # obtaining info such as the files created in the last pull,
    # or the time of the last push

    @property
    def is_active(self) -> bool:
        """
        Is the source currently active.

        A source is considered active if it has an active job.
        The `since` parameter is included to ignore old, orphaned jobs
        which may have not have had their status updated.
        """
        since = datetime.timedelta(minutes=15)
        return (
            self.jobs.filter(
                is_active=True, created__gte=timezone.now() - since
            ).count()
            > 0
        )

    def get_downstreams(self, current=True):
        """
        Get the downstream files.

        The equivalent of `File.get_downstreams()`.
        """
        return self.files.filter(current=current)

    def get_jobs(self, n=10) -> List[Job]:
        """
        Get the jobs associated with this source.
        """
        return self.jobs.order_by("-created").select_related("creator")[:n]

    def save(self, *args, **kwargs):
        """
        Save the source.

        An override to ensure necessary fields are set.
        """
        if not self.address:
            self.address = self.make_address()

        return super().save(*args, **kwargs)


# Source classes in alphabetical order


class ElifeSource(Source):
    """An article from https://elifesciences.org."""

    article = models.IntegerField(help_text="The article number.")

    version = models.IntegerField(
        null=True,
        blank=True,
        help_text="The article version. If blank, defaults to the latest.",
    )

    def make_address(self) -> str:
        """Make the address string of an eLife source."""
        return "elife://{article}".format(article=self.article)

    def get_url(self, path: Optional[str] = None) -> str:
        """Make the URL of the article on the eLife website."""
        return "https://elifesciences.org/articles/{article}".format(
            article=self.article
        )


class GithubSource(Source):
    """A project hosted on Github."""

    repo = models.CharField(
        max_length=512,
        null=False,
        blank=False,
        help_text="The Github repository identifier i.e. org/repo",
    )

    subpath = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="Path to file or folder within the repository",
    )

    def make_address(self) -> str:
        """Make the address string of a GitHub source."""
        return (
            "github://"
            + self.repo
            + ("/{}".format(self.subpath) if self.subpath else "")
        )

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = False, strict: bool = False
    ) -> Optional[SourceAddress]:
        """Parse a string into a GitHub `SourceAddress`."""
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

    def get_url(self, path: Optional[str] = None) -> str:
        """Get the URL of a GitHub source."""
        url = "https://github.com/{}".format(self.repo)
        if self.subpath or path:
            url += os.path.join("/blob/master", self.subpath or "", path or "")
        return url

    def get_secrets(self, user: User) -> Dict:
        """
        Get GitHub API token.

        Will use the token of the source's creator if available, falling back
        to request user's token.
        """
        token = None

        if self.creator:
            token = get_user_social_token(self.creator, Provider.github)

        if token is None and user and user.is_authenticated:
            token = get_user_social_token(user, Provider.github)

        return dict(token=token.token if token else None)


class GoogleSourceMixin:
    """
    Mixin class for all Google related sources.
    """

    creator: User

    def get_secrets(self, user: User) -> Dict:
        """
        Get Google OAuth2 credentials.

        Will use the credentials of the source's creator if
        available, falling back to those of the request's user.
        """
        token = None

        if getattr(self, "creator", None):
            token = get_user_social_token(self.creator, Provider.google)

        if token is None and user and user.is_authenticated:
            token = get_user_social_token(user, Provider.google)

        try:
            app = SocialApp.objects.get(provider=Provider.google.name)
        except SocialApp.DoesNotExist:
            app = None

        return dict(
            access_token=token.token if token else None,
            refresh_token=token.token_secret if token else None,
            client_id=app.client_id if app else None,
            client_secret=app.secret if app else None,
        )


class GoogleDocsSource(GoogleSourceMixin, Source):
    """A reference to a Google Docs document."""

    doc_id = models.TextField(
        null=False,
        help_text="The id of the document e.g. 1iNeKTanIcW_92Hmc8qxMkrW2jPrvwjHuANju2hkaYkA",
    )

    def make_address(self) -> str:
        """Make the address string of a Google Doc source."""
        return "gdoc://{}".format(self.doc_id)

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = False, strict: bool = False
    ) -> Optional[SourceAddress]:
        """Parse a string into a Google Doc address."""
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
            if not re.match(r"^([a-z\d])([a-z\d_\-]{10,})$", doc_id, re.I):
                doc_id = None

        if doc_id:
            return SourceAddress("GoogleDocs", doc_id=doc_id)

        if strict:
            raise ValidationError("Invalid Google Doc identifier: {}".format(address))

        return None

    def get_url(self, path: Optional[str] = None) -> str:
        """Make the URL of a Google Doc."""
        return "https://docs.google.com/document/d/{}/edit".format(self.doc_id)


class GoogleDriveKind(EnumChoice):
    """Enumeration of the kinds of Google Drive resources."""

    file = "File"
    folder = "Folder"


class GoogleDriveSource(GoogleSourceMixin, Source):
    """A reference to a Google Drive file or folder."""

    kind = models.CharField(
        max_length=16,
        choices=GoogleDriveKind.as_choices(),
        help_text="The kind of Google Drive resource: file or folder.",
    )

    google_id = models.TextField(null=False, help_text="The id of the file or folder.")

    def make_address(self) -> str:
        """Make the address string of a Google Drive source."""
        return "gdrive://{kind}/{id}".format(kind=self.kind, id=self.google_id)

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = True, strict: bool = False
    ) -> Optional[SourceAddress]:
        """Parse a string into a Google Drive address."""
        google_id = None

        match = re.search(r"^gdrive://(file|folder)/(.+)$", address, re.I)
        if match:
            kind = match.group(1)
            google_id = match.group(2)

        match = re.search(
            r"^(?:https://)?drive.google.com/file/d/([^/]+)/?.*", address, re.I
        )
        if match:
            kind = "file"
            google_id = match.group(1)

        match = re.search(
            r"^(?:https://)?drive.google.com/drive(?:.*?)/folders/([^/]+)/?.*",
            address,
            re.I,
        )
        if match:
            kind = "folder"
            google_id = match.group(1)

        if google_id:
            return SourceAddress("GoogleDrive", kind=kind, google_id=google_id)

        if strict:
            raise ValidationError("Invalid Google Drive address: {}".format(address))

        return None

    def get_url(self, path: Optional[str] = None) -> str:
        """Make the URL of a Google Drive file or folder."""
        return (
            "https://drive.google.com/"
            + ("file/d/" if self.kind == "file" else "drive/folders/")
            + self.google_id
        )


class PlosSource(Source):
    """An article from https://journals.plos.org."""

    article = models.TextField(help_text="The article DOI.")

    def make_address(self) -> str:
        """Make the address string of a PLOS source."""
        return "plos://{article}".format(article=self.article)

    def get_url(self, path: Optional[str] = None) -> str:
        """Make the URL of a PLOS article."""
        # TODO: Implement fully (see how worker pull_plos.py resolves an article URL)
        return "https://plos.org"


def upload_source_path(instance, filename):
    """
    Get the path to upload the file to.

    To avoid a lot of files in a single directory,
    nests within project.
    """
    return "projects/{project}/sources/upload-{id}-{filename}".format(
        project=instance.project.id, id=instance.id, filename=filename
    )


class UploadSource(Source):
    """
    A file that has been uploaded to the Hub.

    This allows us to keep track of files that have been explicitly
    uploaded to the project folder (as opposed to having been pulled
    from another type of source, or being derived from jobs e.g. conversion).

    During development, uploaded files are stored on the local
    filesystem. In production, they are stored in cloud storage
    e.g. Google Could Storage or S3.

    In addition to the `file` field, we store the other useful attributes
    on a an `UploadedFile`. e.g. `name`, `size`
    See https://docs.djangoproject.com/en/3.0/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    """

    file = models.FileField(
        storage=uploads_storage(),
        upload_to=upload_source_path,
        help_text="The uploaded file.",
    )

    name = models.TextField(
        null=True, blank=True, help_text="The name of the uploaded file."
    )

    size = models.IntegerField(
        null=True, blank=True, help_text="The size of the uploaded file in bytes."
    )

    content_type = models.TextField(
        null=True,
        blank=True,
        help_text="The content type (MIME type) of the uploaded file.",
    )

    def make_address(self) -> str:
        """Make the address string of an upload source."""
        return "upload://{}".format(self.path)

    def get_url(self, path: Optional[str] = None) -> Optional[str]:
        """
        Make the URL of an upload article.

        During development, points to the local file. In production,
        points to the remote location e.g. bucket URL. This should be
        on a different domain, to avoid serving of malicious content
        with XSS from the hub.
        """
        try:
            return self.file.url
        except ValueError:
            # If "The 'file' attribute has no file associated with it." yet
            # then just return None, so that the URL gets updated when in does.
            return None

    def to_address(self):
        """
        Override base method to return address based on the storage being used.

        Returns the appropriate address to pull the uploaded file
        into the project's working directory from either local filesystem
        (dev) or from a URL (e.g. bucket; prod).
        """
        if isinstance(self.file.storage, FileSystemStorage):
            return dict(type="upload", path=self.file.path)
        else:
            return dict(type="upload", url=self.file.url)

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = False, strict: bool = False
    ) -> Optional[SourceAddress]:
        """Parse a string into a upload address."""
        match = re.search(r"^upload://(.+)$", address, re.I)
        if match:
            return SourceAddress("Upload", name=match.group(1))

        if strict:
            raise ValidationError(
                "Invalid upload source identifier: {}".format(address)
            )

        return None

    @staticmethod
    def create_or_update_from_uploaded_file(
        user: User, project: Project, path: str, file: UploadedFile
    ) -> "UploadSource":
        """
        Create or update a `UploadSource` from an uploaded file.

        This method is analogous to the API's `SourceSerializer.create`
        in that it creates a pull job. This is not part of the API because of
        the different semantics (re-uploads a file if it already exists).
        """
        try:
            source = UploadSource.objects.get(project=project, path=path)
        except UploadSource.DoesNotExist:
            source = UploadSource(project=project, path=path)

        source.file = file
        source.name = file.name
        source.size = file.size
        source.content_type = file.content_type
        source.save()

        job = source.pull(user)
        job.dispatch()

        return source


class UrlSource(Source):
    """
    A source that is downloaded from a URL on demand.
    """

    url = models.URLField(null=False, blank=False, help_text="The URL of the source.",)

    def make_address(self) -> str:
        """Get the address of a URL source."""
        return self.url

    def get_url(self, path: Optional[str] = None) -> str:
        """Make the URL of a URL source."""
        return self.url

    @classmethod
    def parse_address(
        cls, address: str, naked: bool = False, strict: bool = False
    ) -> Optional[SourceAddress]:
        """Parse a string into a URL `SourceAddress`."""
        url: Optional[str] = address
        try:
            URLValidator()(url)
        except ValidationError:
            url = None

        if url:
            return SourceAddress("Url", url=url)

        if strict:
            raise ValidationError("Invalid URL source: {}".format(address))

        return None


@unique
class SourceTypes(Enum):
    """
    Enumeration of the types of project sources.
    """

    ElifeSource = ElifeSource
    GithubSource = GithubSource
    GoogleDocsSource = GoogleDocsSource
    GoogleDriveSource = GoogleDriveSource
    PlosSource = PlosSource
    UploadSource = UploadSource
    UrlSource = UrlSource
