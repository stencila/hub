import datetime
import hashlib
import secrets
import typing
from io import BytesIO

from django.conf import settings
from django.db import models
from django_extensions.db.fields.json import JSONField

from accounts.models import Account
from lib.data_cleaning import SlugType, clean_slug
from lib.enum_choice import EnumChoice
from lib.path_operations import utf8_dirname, relative_path_join
from projects.source_models import Source
from projects.validators import validate_publish_url_path

TOKEN_HASH_FUNCTION = hashlib.sha256
PROJECT_KEY_LENGTH = 32
TRUNCATED_TOKEN_SHOW_CHARACTERS = 8


def generate_project_key() -> str:
    """Generate a random key for a SessionGroup."""
    return secrets.token_hex(PROJECT_KEY_LENGTH)


def generate_project_token(project: 'Project') -> str:
    """Generate a unique token for a Project based on its creator, creation date and a random string."""
    user_id = project.creator.id if project.creator else None
    created = project.created or datetime.datetime.now()
    return TOKEN_HASH_FUNCTION("{}{}{}".format(user_id, created, secrets.token_hex()).encode("utf8")).hexdigest()


class Project(models.Model):
    class Meta:
        unique_together = [['name', 'account'], ['id', 'snapshot_in_progress']]

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='projects',
        null=False,
        blank=False
    )

    name = models.SlugField(
        null=False,
        blank=False,
        help_text="Name of the project, an identifier used in URLs. Must be unique within the Project's account"
    )

    creator = models.ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=models.SET_NULL,
        related_name='projects_created',
        help_text='User who created project'
    )

    created = models.DateTimeField(
        auto_now_add=True,
        help_text='When this project was created'
    )

    public = models.BooleanField(
        default=False,
        help_text='Should this project be publicly visible?'
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Brief description of the project"
    )

    token = models.TextField(
        null=True,
        blank=True,
        unique=True,
        help_text='A token to identify this project (in URLs etc)'
    )

    key = models.TextField(
        null=True,
        blank=True,
        help_text='Key required to create sessions for this project'
    )

    sessions_total = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum total number of sessions that can be created for this project (null = unlimited)'
    )

    sessions_concurrent = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum number of sessions allowed to run at one time for this project (null = unlimited)',
    )

    sessions_queued = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum number of queued requests for a session for this project (null = unlimited)'
    )

    session_parameters = models.ForeignKey(
        'SessionParameters',
        related_name='projects',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='The parameters that defines sessions created for this project'
    )

    main_file_path = models.TextField(
        null=True,
        blank=True,
        help_text='The path to the main file of the Project. Does not need to be set.'
    )

    main_file_source = models.ForeignKey(
        'Source',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='main_file_project',
        help_text='If the Project\'s main file is inside a linked Source, this is its id.'

    )

    snapshot_in_progress = models.BooleanField(
        default=False,
        help_text='Should be set true when a Snapshot begins for a project.'
    )

    def __str__(self):
        return self.name

    @staticmethod
    def create(project_type, creator):
        """
        Create a new editor of the given project_type.

        TODO: is this, and the following few methods, necessary?
        """
        raise NotImplementedError()

    @staticmethod
    def get_or_create(project_type, address, creator):
        """Get, or create, a project."""
        return Project.objects.get_or_create(
            address=address,
            creator=creator
        )

    @staticmethod
    def get_or_create_from_address(address, creator):
        """Get, or create, a project from an address."""
        # TODO Transform the address into type etc
        return Project.get_or_create(
            address=address,
            creator=creator
        )

    @staticmethod
    def get_or_create_from_url(url, creator):
        """
        Get, or create, a project from a URL.

        This method enables users to specify a project
        by copying a third party URL from the browser address bar.
        Converts the URL into an address. For example,

        https://github.com/stencila/examples/tree/master/mtcars

        is converted to,

        github://stencila/examples/mtcars
        """
        # TODO Transform the URL into an address
        address = url
        return Project.get_or_create_from_address(address, creator)

    def get_name(self):
        """Temporary implementation of a name property which is likely to be replaced by a db field in future."""
        return self.name or 'Unnamed'

    def get_first_source(self) -> Source:
        source = self.sources.first()  # TODO: Update this when UI supports multiple sources
        if not source:
            raise ValueError("This project has no sources")

        return source

    def pull(self) -> BytesIO:
        """Pull files from the project source."""
        return self.get_first_source().pull()

    def push(self, archive: typing.IO) -> None:
        """Push files to the project source."""
        self.get_first_source().push(archive)

    def save(self, *args, **kwargs) -> None:
        self.name = clean_slug(self.name, SlugType.PROJECT)

        if not self.token:
            self.token = generate_project_token(self)

        if not self.session_parameters:
            from projects.session_models import SessionParameters
            self.session_parameters = SessionParameters.objects.create()

        super().save(*args, **kwargs)

    @property
    def truncated_token(self) -> str:
        """Chop out the middle of the token for short display."""
        return "{}...{}".format(self.token[:TRUNCATED_TOKEN_SHOW_CHARACTERS],
                                self.token[-TRUNCATED_TOKEN_SHOW_CHARACTERS:])

    # TODO: the `_pull` and `_push` methods below are just saved from a previous
    # iteration of FilesSource, not sure we'll want to keep them.

    def _pull(self) -> BytesIO:
        """Pull files from the Django storage into an archive."""
        from zipfile import ZipFile

        # Write all the files into a zip archive
        archive = BytesIO()
        with ZipFile(archive, 'w') as zipfile:
            for file in self.files.all():
                # For remote storages (e.g. Google Cloud Storage buckets)
                # `file.file.path` is not available, so use `file.file.read()`
                zipfile.writestr(file.name, file.file.read())
        return archive

    def _push(self, archive: typing.Union[str, typing.IO]) -> None:
        """Push files in the archive to the Django storage."""
        from .disk_file_facade import DiskFileFacade  # late import to break dependency loop
        from zipfile import ZipFile

        # Unzip all the files and add to this project
        zipfile = ZipFile(archive, 'r')
        for name in zipfile.namelist():
            # Replace existing file or create a new one
            dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, self)
            dff.write_file_content(name, zipfile.read(name))

    @property
    def has_url_published_items(self) -> bool:
        return self.published_items.filter(url_path__isnull=False).exclude(url_path='').count() != 0


class ProjectEventType(EnumChoice):
    SOURCE_PULL = 'SOURCE_PULL'
    ARCHIVE = 'ARCHIVE'
    SNAPSHOT = 'SNAPSHOT'


PROJECT_EVENT_LONG_TYPE_LOOKUP = {
    ProjectEventType.SOURCE_PULL.name: 'Source Pull to Disk',  # type: ignore # mypy does not understand enums
    ProjectEventType.ARCHIVE.name: 'Archive',  # type: ignore # mypy does not understand enums
    ProjectEventType.SNAPSHOT.name: 'Snapshot'  # type: ignore # mypy does not understand enums
}


class ProjectEventLevel(EnumChoice):
    # Don't renumber these (adding more is fine) as it will change the relationship of the existing records
    EMERGENCY = 0
    ALERT = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = 4
    NOTICE = 5
    INFORMATIONAL = 6
    DEBUG = 7


class ProjectEvent(models.Model):
    event_type = models.TextField(null=False,
                                  blank=False,
                                  choices=ProjectEventType.as_choices()
                                  )

    started = models.DateTimeField(
        null=False,
        blank=False,
        auto_now_add=True,
        help_text='DateTime this Event started.'
    )

    finished = models.DateTimeField(
        null=True,
        blank=True,
        help_text='DateTime this Event finished. If null assume it is still running.'
    )

    message = models.TextField(
        null=True,
        blank=True,
        help_text='A message associated with this Event, may be an error message or some information or blank.'
    )

    success = models.BooleanField(
        null=True,
        blank=True,
        help_text='Indicates if the event finished with success or not. If the Event is still in progress then success '
                  'will be null.'
    )

    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                null=False,
                                related_name='events',
                                help_text='The Project that this Event is for.'
                                )

    user = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        help_text='The user who performed/triggered this event.',
        on_delete=models.SET_NULL
    )

    level = models.IntegerField(null=False, default=ProjectEventLevel.INFORMATIONAL.value,
                                choices=ProjectEventLevel.as_choices(), help_text='The "log level" of the event.')

    # There's no JSON field that automatically uses TEXT storage in dev (SQLite) then switches to native JSON in
    # production (PostgreSQL), so just use a non-native one. If Django ever implements such a feature then we should
    # consider migrating
    log = JSONField(null=True, blank=True, help_text='Log messages, in the DB they are stored as text but are '
                                                     'automatically JSON (de)serialized on writing/reading.')

    class Meta:
        ordering = ['-started']

    @property
    def long_type(self) -> str:
        return PROJECT_EVENT_LONG_TYPE_LOOKUP.get(self.event_type, 'Unknown')


class Snapshot(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text='Project this snapshot belongs to.',
                                related_name='snapshots')
    path = models.TextField(help_text='The path to the snapshot directory on disk.')
    created = models.DateTimeField(auto_now_add=True, help_text='The date/time the Snapshot instance was created.')
    snapshot_time = models.DateTimeField(null=True, blank=True, help_text='The time that Snapshot operation happened, '
                                                                          'null if the snapshot has not yet been '
                                                                          'performed.')
    version_number = models.PositiveIntegerField(verbose_name='Each snapshot should have an incremental version.')
    tag = models.SlugField(null=True, blank=True, help_text='A tag to identify the snapshot easily. Must be unique for '
                                                            'the project.')

    class Meta:
        unique_together = (('project', 'version_number'), ('project', 'tag'))


class PublishedItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text='Project this item belongs to.',
                                related_name='published_items')
    path = models.TextField(blank=True, null=True,
                            help_text='The full path to the published file (in HTML format).')
    url_path = models.TextField(blank=True, null=True,
                                help_text='The path used to access the published item on the web, relative to the '
                                          'account/project.', validators=[validate_publish_url_path])
    created = models.DateTimeField(auto_now_add=True, help_text='The date/time the item was first published.')
    updated = models.DateTimeField(auto_now=True, help_text='The date/time the item was last published.')
    source = models.ForeignKey(Source, on_delete=models.DO_NOTHING, null=True,
                               help_text='The source item of this publication. May be null for a DiskSource.')
    source_path = models.TextField(help_text='The relative path of the file that was published. Relative to its '
                                             'Project or snapshot root.')
    snapshot = models.ForeignKey(Snapshot, blank=True, null=True, on_delete=models.CASCADE,
                                 help_text='The snapshot that contains the original source. Null for PublishedItems '
                                           'created from non-snapshot files.')

    class Meta:
        unique_together = (('project', 'url_path'),)

    def save(self, *args, **kwargs):
        # Remove leading/trailing / in URL path
        if self.url_path:
            self.url_path = self.url_path.strip('/')
        super(PublishedItem, self).save(*args, **kwargs)

    def media_path(self, path: str) -> str:
        media_path = '{}.html.media/{}'.format(self.pk, path)
        return relative_path_join(utf8_dirname(self.path), media_path)
