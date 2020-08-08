import enum
import mimetypes
from datetime import datetime
from typing import Dict, List, NamedTuple, Optional, Tuple

import httpx
import pygments
import pygments.lexers
from django.db import models, transaction
from django.http import FileResponse, HttpResponse
from django.shortcuts import reverse
from django.utils import timezone

from jobs.models import Job, JobMethod
from manager.storage import FileSystemStorage, snapshots_storage, working_storage
from projects.models.projects import Project
from projects.models.sources import Source
from users.models import User

SNAPSHOTS_STORAGE = snapshots_storage()
SNAPSHOT_STORAGE_CLIENT = httpx.Client()
WORKING_STORAGE = working_storage()


class FileFormat(NamedTuple):
    """
    Specification of a file format.

    The `format_id` should be a lowercase string and
    map to a "codec" in Encoda.
    In the future, these specs may be generated from Encoda
    codec modules which also define the equivalent of
    `mimetypes` and `extensions`.
    """

    format_id: str
    label: str
    kind: str
    mimetype: str
    extensions: List[str]
    icon_class: str
    minor: bool = False

    @property
    def default_extension(self) -> str:
        """Get the default extension for the format."""
        return self.extensions[0] if self.extensions else ("." + self.format_id)

    @staticmethod
    def default_icon_class() -> str:
        """Get the default icon class."""
        return "ri-file-3-line"

    @property
    def is_binary(self) -> bool:
        """Is the format be considered binary when determining the type of HTTP response."""
        return self.format_id not in ("html", "json", "jsonld", "md", "rmd", "xml")

    @property
    def convert_to_options(self) -> List[Tuple[str, str]]:
        """
        Get a list of file formats that a user can convert to from the given format.
        """
        if self.kind in ("exchange", "text"):
            to_kinds = ("exchange", "text")
        else:
            return []

        return [
            f.value
            for f in FileFormats
            if f.value.kind in to_kinds and not f.value.minor
        ]

    @staticmethod
    def default_convert_to_options() -> List["FileFormat"]:
        """Get the default options for converting the format to."""
        return [f.value for f in FileFormats if not f.value.minor]


def file_format(
    format_id: str,
    label: Optional[str] = None,
    kind: Optional[str] = None,
    mimetype: Optional[str] = None,
    extensions: Optional[List[str]] = None,
    icon_class: Optional[str] = None,
    minor: bool = False,
):
    """
    Create a `FileFormat` with fallbacks.

    Necessary because you can't override `__init__` for a
    named tuple.
    """
    if label is None:
        label = format_id.upper()

    if mimetype is None:
        mimetype, encoding = mimetypes.guess_type("file." + format_id)
        if mimetype is None:
            raise RuntimeError(
                "Can not guess a MIME type for format {0}".format(format_id)
            )

    if extensions is None:
        extensions = mimetypes.guess_all_extensions(mimetype)

    if kind is None:
        if mimetype.startswith("image/"):
            kind = "image"
        else:
            kind = "text"

    if icon_class is None:
        if mimetype.startswith("image/"):
            icon_class = "ri-image-line"
        else:
            icon_class = FileFormat.default_icon_class()

    return FileFormat(format_id, label, kind, mimetype, extensions, icon_class, minor)


class FileFormats(enum.Enum):
    """
    List of file formats.

    When adding `icon_class`es below, note that they may need to be
    added to the `purgecss` whitelist in `postcss.config.js` to
    avoid them from being purged (if they are not used in any of the HTNL templates)
    """

    docx = file_format("docx", label="Microsoft Word", icon_class="ri-file-word-line")
    gdoc = file_format(
        "gdoc",
        label="Google Doc",
        mimetype="application/vnd.google-apps.document",
        icon_class="ri-google-line",
    )
    gif = file_format("gif", icon_class="ri-file-gif-line")
    html = file_format("html")
    ipynb = file_format(
        "ipynb", label="Jupyter Notebook", mimetype="application/x-ipynb+json"
    )
    jats = file_format(
        "jats",
        label="JATS XML",
        mimetype="application/jats+xml",
        extensions=[".jats.xml"],
    )
    jpg = file_format("jpg")
    json = file_format("json", kind="exchange", minor=True)
    json5 = file_format(
        "json5", mimetype="application/json5", kind="exchange", minor=True
    )
    jsonld = file_format(
        "jsonld", label="JSON-LD", mimetype="application/ld+json", kind="exchange"
    )
    md = file_format(
        "md", label="Markdown", mimetype="text/markdown", icon_class="ri-markdown-line"
    )
    odt = file_format("odt")
    pandoc = file_format(
        "pandoc",
        label="Pandoc JSON",
        mimetype="application/pandoc+json",
        kind="exchange",
        minor=True,
    )
    pdf = file_format("pdf", icon_class="ri-file-pdf-line")
    png = file_format("png")
    rmd = file_format("rmd", label="R Markdown", mimetype="text/r+markdown")
    rnb = file_format(
        "rnb", mimetype="text/rstudio+html", extensions=[".nb.html"], minor=True
    )
    text = file_format("txt", label="Plain text")
    yaml = file_format("yaml", mimetype="application/x-yaml", kind="exchange")
    xlsx = file_format("xlsx", kind="spreadsheet", icon_class="ri-file-excel-line")
    xml = file_format("xml", kind="exchange", minor=True)

    @classmethod
    def from_id(cls, format_id: str) -> "FileFormat":
        """
        Get a file format from it's id.
        """
        for f in cls:
            if f.value.format_id == format_id:
                return f.value

        raise ValueError("No such member with id {}".format(format_id))

    @classmethod
    def from_mimetype(cls, mimetype: str) -> "FileFormat":
        """
        Get a file format from it's MIME type.
        """
        for f in cls:
            if mimetype == f.value.mimetype:
                return f.value

        raise ValueError("No such member with mimetype {}".format(mimetype))

    @classmethod
    def from_id_or_mimetype(
        cls, format_id: Optional[str] = None, mimetype: Optional[str] = None
    ) -> "FileFormat":
        """
        Get a file format from it's id or MIME type.
        """
        if format_id:
            return FileFormats.from_id(format_id)
        elif mimetype:
            return FileFormats.from_mimetype(mimetype)
        else:
            raise ValueError("Must provide format id or MIME type")


class File(models.Model):
    """
    A file associated with a project.

    Files are created by a `job` and may be derived from a `source`,
    or from another `upstream` file.

    A `File` object (i.e. a row in the corresponding database table) is
    never deleted. Instead, it is made `current=False`. That allows us
    to easily maintain a history of each file in a project.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="files",
        null=False,
        blank=False,
        help_text="The project that the file is associated with.",
    )

    path = models.TextField(
        null=False,
        blank=False,
        db_index=True,
        help_text="The path of the file within the project.",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
        help_text="The job that created the file e.g. a source pull or file conversion.",
    )

    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="files",
        help_text="The source from which the file came (if any). "
        "If the source is removed from the project, so will this file.",
    )

    upstreams = models.ManyToManyField(
        "File",
        related_name="downstreams",
        help_text="The files that this file was derived from (if any).",
    )

    snapshot = models.ForeignKey(
        "Snapshot",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="files",
        help_text="The snapshot that the file belongs. "
        "If the snapshot is deleted so will the files.",
    )

    current = models.BooleanField(
        default=True,
        help_text="Is the file currently in the project? "
        "Used to retain a history for file paths within a project.",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="The time the file info was created."
    )

    updated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The time the file info was updated. "
        "This field will have the last time this row was altered (i.e. changed from current, to not).",
    )

    modified = models.DateTimeField(
        null=True, blank=True, help_text="The file modification time."
    )

    size = models.PositiveIntegerField(
        null=True, blank=True, help_text="The size of the file in bytes",
    )

    mimetype = models.CharField(
        max_length=512, null=True, blank=True, help_text="The mimetype of the file.",
    )

    encoding = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text="The encoding of the file e.g. gzip",
    )

    fingerprint = models.CharField(
        max_length=128, null=True, blank=True, help_text="The fingerprint of the file",
    )

    @staticmethod
    @transaction.atomic
    def create(
        project: Project,
        path: str,
        info: Dict,
        job: Optional[Job] = None,
        source: Optional[Source] = None,
        upstreams: List["File"] = [],
        snapshot=None,
    ) -> "File":
        """
        Create a file within a project.

        Jobs return a dictionary of file information for each
        file that has been updated. This creates a `File` instance based
        on that informaton.

        If a file with the same path already exists in the project, then
        it is made `current=False`.
        """
        if snapshot:
            current = False
        else:
            File.objects.filter(project=project, path=path, current=True).update(
                current=False, updated=timezone.now()
            )
            current = True

        file = File.objects.create(
            project=project,
            path=path,
            current=current,
            job=job,
            source=source,
            snapshot=snapshot,
            modified=get_modified(info),
            size=info.get("size"),
            mimetype=info.get("mimetype"),
            encoding=info.get("encoding"),
            fingerprint=info.get("fingerprint"),
        )
        if upstreams:
            file.upstreams.set(upstreams)

        return file

    def remove(self):
        """
        To keep the file history we do not actually remove the file but make it not current.
        """
        self.current = False
        self.updated = timezone.now()
        self.save()

    def get_upstreams(self, current=True):
        """
        Get the upstream source or files.
        """
        return [self.source] if self.source else self.upstreams.filter(current=current)

    def get_downstreams(self, current=True):
        """
        Get the downstream files.
        """
        return self.downstreams.filter(current=current)

    def open_url(self) -> Optional[str]:
        """
        Get a URL to open the file at the source.

        Currently, simply returns the URL to "open" the `source` (if any).
        In the future, each source type should provide a URL to edit a
        particular file from a multi-file source (e.g. a file within a Github repo).

        Does not provide the URL of the source directly because that would
        require additional queries to the table for each source type (instead provides URL
        to API endpoint which will redirect to the URL).

        Intentionally returns `None` for files in a snapshot (they do not have a `source`).
        """
        return (
            reverse(
                "api-projects-sources-open",
                kwargs=dict(project=self.project_id, source=self.source_id),
            )
            if self.source_id
            else None
        )

    def get_lexer(self):
        """
        Get a Pygments lexer for the file.

        Returns `None` if no matching lexer can be found.
        """
        try:
            return pygments.lexers.guess_lexer_for_filename(self.path, "")
        except pygments.util.ClassNotFound:
            try:
                return pygments.lexers.get_lexer_for_mimetype(self.mimetype)
            except pygments.util.ClassNotFound:
                return None

    def highlight_content(self) -> Optional[Tuple[str, str]]:
        """
        Highlight the content of the file.

        Returns `None` if the content can not be highlighted.
        """
        lexer = self.get_lexer()
        if not lexer:
            return None

        content = self.get_content()
        formatter = pygments.formatters.HtmlFormatter(
            cssclass="source", style="colorful"
        )
        css = formatter.get_style_defs(".highlight")
        html = pygments.highlight(content, lexer, formatter)
        return css, html

    def highlight_url(self) -> Optional[str]:
        """
        Get a URL to view the syntax highlighted content of the file (if possible).

        Returns `None` if the content can not be highlighted.
        """
        if self.get_lexer():
            return reverse(
                "ui-projects-files-highlight",
                kwargs=dict(
                    account=self.project.account.name,
                    project=self.project.name,
                    file=self.path,
                ),
            )
        else:
            return None

    def download_url(self) -> str:
        """
        Get a URL to download the file.

        This just returns the project's `content_url`, including necessary
        snapshot path and keys (for private projects).
        """
        if self.snapshot:
            return self.project.content_url(snapshot=self.snapshot, path=self.path)
        else:
            return self.project.content_url(live=True, path=self.path)

    def get_response(self, limit_rate: Optional[str] = "off") -> HttpResponse:
        """
        Return a HTTP response to get this file.
        """
        if self.snapshot:
            if isinstance(self.snapshot.STORAGE, FileSystemStorage):
                # Read the file from the filesystem.
                # Normally this will only be used during development!
                location = self.snapshot.file_location(self.path)
                file = self.snapshot.STORAGE.open(location)
                return FileResponse(file)
            else:
                # In production, send the the `X-Accel-Redirect` and other headers
                # so that Nginx will reverse proxy
                url = self.snapshot.file_url(self.path)
                response = HttpResponse()
                response["X-Accel-Redirect"] = "@account-content"
                response["X-Accel-Redirect-URL"] = url
                response["X-Accel-Limit-Rate"] = limit_rate
                return response
        else:
            location = self.project.file_location(self.path)
            file = self.project.STORAGE.open(location)
            return FileResponse(file)

    def get_content(self) -> bytes:
        """
        Get the content of this file.

        The link will vary depending upon if the file is in the project's
        working directory, or if it is in a project snapshot.
        """
        if self.snapshot:
            if isinstance(self.snapshot.STORAGE, FileSystemStorage):
                # Read the file from the filesystem.
                # Normally this will only be used during development!
                location = self.snapshot.file_location(self.path)
                with self.snapshot.STORAGE.open(location) as file:
                    return file.read()
            else:
                # Fetch the file from storage and send it on to the client
                url = self.snapshot.file_url(self.path)
                return SNAPSHOT_STORAGE_CLIENT.get(url).content
        else:
            location = self.project.file_location(self.path)
            with self.project.STORAGE.open(location) as file:
                return file.read()

    def convert(self, user: User, output: str) -> Job:
        """
        Convert a file to another format.

        Creates a `convert` job which returns a list of files produced
        (may be more than one e.g a file with a media folder). Each of the
        produced files will have this file as a dependency.
        """
        return Job.objects.create(
            description="Convert '{0}' to '{1}'".format(self.path, output),
            project=self.project,
            creator=user,
            method=JobMethod.convert.name,
            params=dict(project=self.project.id, input=self.path, output=output),
            **Job.create_callback(self, "convert_callback"),
        )

    @transaction.atomic
    def convert_callback(self, job: Job):
        """
        Add the created files to the project and make this file the upstream of each.
        """
        result = job.result
        if not result:
            return

        for path, info in result.items():
            File.create(self.project, path, info, job=job, upstreams=[self])


class FileDownloads(models.Model):
    """
    Download metrics by day for a file.

    These metrics are principally stored to be able to restrict (i.e. prevent
    or throttle) file downloads for a project once they reach a monthly limit.
    For storage and compute efficiency we do not try to use them for user
    facing analytics which would be inaccurate in any case due to caching headers etc.

    The total number of bytes downloaded for the file in the month can be
    calculated using this `count` and its `File.size`.
    """

    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name="downloads",
        help_text="The file that these download metrics relate to.",
    )

    month = models.CharField(
        db_index=True,
        max_length=7,
        help_text="The calendar month, in YYYY-MM format, that these download metrics relate to.",
    )

    count = models.PositiveIntegerField(
        help_text="The number of downloads for the file for the month."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["file", "month"], name="%(class)s_unique_file_month"
            )
        ]


def get_modified(info: Dict) -> Optional[datetime]:
    """
    Get the modified data as a timezone aware datetime object.
    """
    timestamp = info.get("modified")
    return datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else None
