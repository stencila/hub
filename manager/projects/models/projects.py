import datetime
import os
from typing import Dict, List, Optional
from urllib.parse import urlencode

import shortuuid
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.http import HttpRequest
from django.shortcuts import reverse
from django.utils import timezone
from meta.views import Meta

from accounts.models import Account, AccountTeam
from jobs.models import Job, JobMethod
from manager.helpers import EnumChoice
from manager.storage import StorageUsageMixin, media_storage, working_storage
from users.models import User


class ProjectLiveness(EnumChoice):
    """
    Where the project content is served from.
    """

    LIVE = "live"
    LATEST = "latest"
    PINNED = "pinned"

    @staticmethod
    def as_choices():
        """Return as a list of field choices."""
        return (
            # Live is currently disabled as a choice
            # pending implementation
            ("live", "Use working directory"),
            ("latest", "Use latest snapshot"),
            ("pinned", "Pinned to snapshot"),
        )


def generate_project_key():
    """
    Generate a unique, and very difficult to guess, project key.
    """
    return shortuuid.ShortUUID().random(length=32)


class Project(StorageUsageMixin, models.Model):
    """
    A project.

    Projects are always owned by an account.
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="projects",
        null=False,
        blank=False,
        help_text="Account that the project belongs to.",
    )

    creator = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="projects_created",
        help_text="The user who created the project.",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="The time the project was created."
    )

    name = models.SlugField(
        null=False,
        blank=False,
        help_text="Name of the project. Lowercase only and unique for the account. "
        "Will be used in URLS e.g. https://hub.stenci.la/awesome-org/great-project.",
    )

    title = models.CharField(
        null=True,
        blank=True,
        max_length=256,
        help_text="Title of the project to display in its profile.",
    )

    temporary = models.BooleanField(
        default=False, help_text="Is the project temporary?"
    )

    public = models.BooleanField(
        default=True, help_text="Is the project publicly visible?"
    )

    featured = models.BooleanField(
        default=False, help_text="Is the project to be featured in listings?"
    )

    key = models.CharField(
        default=generate_project_key,
        max_length=64,
        help_text="A unique, and very difficult to guess, key to access this project if it is not public.",
    )

    description = models.TextField(
        null=True, blank=True, help_text="Brief description of the project."
    )

    image_file = models.ImageField(
        null=True,
        blank=True,
        storage=media_storage(),
        upload_to="projects/images",
        help_text="The image used for this project in project listings and HTML meta data.",
    )

    image_path = models.CharField(
        null=True,
        blank=True,
        max_length=1024,
        help_text="Path of file in the project's working directory to use as this project's image. "
        "Allows the project's image to update as it is re-executed.",
    )

    image_updated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the image file was last updated (e.g. from image_path).",
    )

    theme = models.TextField(
        null=True,
        blank=True,
        help_text="The name of the theme to use as the default when generating content for this project."
        # See note for the `Account.theme` field for why this is a TextField.
    )

    extra_head = models.TextField(
        null=True,
        blank=True,
        help_text="Content to inject into the <head> element of HTML served for this project.",
    )

    extra_top = models.TextField(
        null=True,
        blank=True,
        help_text="Content to inject at the top of the <body> element of HTML served for this project.",
    )

    extra_bottom = models.TextField(
        null=True,
        blank=True,
        help_text="Content to inject at the bottom of the <body> element of HTML served for this project.",
    )

    container_image = models.TextField(
        null=True,
        blank=True,
        help_text="The container image to use as the execution environment for this project.",
    )

    main = models.TextField(
        null=True, blank=True, help_text="Path of the main file of the project",
    )

    liveness = models.CharField(
        max_length=16,
        choices=ProjectLiveness.as_choices(),
        default=ProjectLiveness.LATEST.value,
        help_text="Where to serve the content for this project from.",
    )

    pinned = models.ForeignKey(
        "Snapshot",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="project_pinned",
        help_text="If pinned, the snapshot to pin to, when serving content.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["account", "name"], name="%(class)s_unique_account_name"
            )
        ]

    TEMPORARY_PROJECT_LIFESPAN = datetime.timedelta(days=1)

    STORAGE = working_storage()

    def __str__(self):
        return self.name

    def get_meta(self) -> Meta:
        """
        Get the metadata to include in the head of the project's pages.
        """
        return Meta(
            object_type="article",
            title=self.title or self.name,
            description=self.description,
            image=self.image_file.url if self.image_file else None,
        )

    def set_image_from_file(self, file):
        """
        Update the image file for the project from the path of a file within it.
        """
        if isinstance(file, str):
            try:
                file = self.files.filter(current=True, path=file)[0]
            except IndexError:
                return

        content = file.get_content()
        format = file.get_format()
        ext = format.default_extension if format else ""

        # The file name needs to be unique to bust any caches.
        file = ContentFile(content)
        file.name = f"{self.id}-{shortuuid.uuid()}{ext}"

        self.image_file = file
        self.image_updated = timezone.now()
        self.save()

    def update_image(self):
        """
        Update the image for the project.
        """
        modified_since = (
            dict(modified__gt=self.image_updated) if self.image_updated else {}
        )
        if self.image_path and self.image_path != "__uploaded__":
            # Does the file need updating?
            images = self.files.filter(
                current=True, path=self.image_path, **modified_since
            ).order_by("-modified")
            if len(images) > 0:
                self.set_image_from_file(images[0])
        else:
            # Try to find an image for the project and use the most
            # recently modified since the image was last updated
            images = self.files.filter(
                current=True, mimetype__startswith="image/", **modified_since,
            ).order_by("-modified")
            if len(images) > 0:
                self.set_image_from_file(images[0])

    def update_image_all_projects(self):
        """
        Update the image of all projects.
        """
        projects = Project.objects.all(temporary=False)
        for project in projects:
            project.update_image()

    @property
    def scheduled_deletion_time(self) -> Optional[datetime.datetime]:
        """
        Get the scheduled deletion time of a temporary project.
        """
        return (
            (self.created + Project.TEMPORARY_PROJECT_LIFESPAN)
            if self.temporary
            else None
        )

    def get_main(self):
        """
        Get the main file for the project.

        The main file can be designated by the user
        (using the `main` field as the path). If no file
        matches that path (e.g. because it was removed),
        or if `main` was never set, then this defaults to the
        most recently modified file with path `main.*` or `README.*`
        if those are present.
        """
        if self.main:
            try:
                # Using `filter()` and indexing to get the first item is more robust that
                # using `get()`. There should only be one item with path that is current
                # but this avoids a `MultipleObjectsReturned` in cases when there is not.
                return self.files.filter(path=self.main, current=True).order_by(
                    "-created"
                )[0]
            except IndexError:
                pass

        candidates = self.files.filter(
            Q(path__startswith="main.") | Q(path__startswith="README."), current=True
        ).order_by("-modified")
        if len(candidates):
            return candidates[0]

        return None

    def get_theme(self) -> str:
        """Get the theme for the project."""
        return self.theme or self.account.theme

    def content_url(self, snapshot=None, path=None, live=False) -> str:
        """
        Get the URL that the content for this project is served on.

        This is the URL, on the account subdomain,
        that content for the project is served from.
        """
        params: Dict = {}
        if settings.CONFIGURATION.endswith("Dev"):
            # In development, it's very useful to be able to preview
            # content, so we return a local URL
            url = (
                reverse("ui-accounts-content", kwargs=dict(project_name=self.name))
                + "/"
            )
            params.update(account=self.account.name)
        else:
            # In production, return an account subdomain URL
            url = "https://{account}.{domain}/{project}/".format(
                account=self.account.name,
                domain=settings.ACCOUNTS_DOMAIN,
                project=self.name,
            )

        # Defaults to generating a URL for the latest snapshot
        # unless specific snapshot, or live is True
        if live:
            url += "live/"
        elif snapshot:
            url += "v{0}/".format(snapshot.number)

        if not self.public:
            url += "~{0}/".format(self.key)
        if path:
            url += path
        if params:
            url += "?" + urlencode(params)

        return url

    def file_location(self, file: str) -> str:
        """
        Get the location of one of the project's files relative to the root of the storage volume.
        """
        return os.path.join(str(self.id), file)

    def event(self, data: dict, source=None):
        """
        Handle an event notification.

        Records the event and evaluates each project trigger.
        """
        ProjectEvent.objects.create(project=self, data=data, source=source)

        # TODO: Evaluate each project trigger
        # #for trigger in self.triggers.all():
        #    trigger.evaluate(event=event, context=dict(event=event, source=source))

    def cleanup(self, user: User) -> Job:
        """
        Clean the project's working directory.

        Removes all files from the working directory.
        In the future, this may be smarter and only remove
        those files that are orphaned (i.e. not registered as part of the pipeline).

        This is not called `clean()` because that clashes with
        `Model.clean()` which gets called, for example, after the submission
        of a form in the admin interface.
        """
        return Job.objects.create(
            description="Clean project '{0}'".format(self.name),
            project=self,
            creator=user,
            method=JobMethod.clean.name,
        )

    def pull(self, user: User) -> Job:
        """
        Pull all sources in the project.

        Creates a `parallel` job having children jobs that `pull`
        each source into the project's working directory.
        """
        job = Job.objects.create(
            description="Pull project '{0}'".format(self.name),
            project=self,
            creator=user,
            method=JobMethod.parallel.name,
        )
        job.children.set([source.pull(user) for source in self.sources.all()])
        return job

    def session(self, request: HttpRequest) -> Job:
        """
        Create a session job for the project.
        """
        job = Job.objects.create(
            method=JobMethod.session.name,
            params=dict(container_image=self.container_image),
            description="Session for project",
            project=self,
            creator=request.user if request.user.is_authenticated else None,
        )
        job.add_user(request)
        return job


def make_project_creator_an_owner(
    sender, instance: Project, created: bool, *args, **kwargs
):
    """
    Make the project create an owner.

    Makes sure each project has at least one owner.
    """
    if sender is Project and created and instance.creator:
        ProjectAgent.objects.create(
            project=instance, user=instance.creator, role=ProjectRole.OWNER.name
        )


post_save.connect(make_project_creator_an_owner, sender=Project)


class ProjectRole(EnumChoice):
    """
    A user or team role within an account.

    See `get_description` for what each role can do.
    Some of roles can also be applied to the public.
    For example, a project might be made public with
    the `REVIEWER` role allowing anyone to comment.
    """

    READER = "Reader"
    REVIEWER = "Reviewer"
    EDITOR = "Editor"
    AUTHOR = "Author"
    MANAGER = "Manager"
    OWNER = "Owner"

    @classmethod
    def get_description(cls, role: "ProjectRole"):
        """Get the description of a project role."""
        return {
            cls.READER.name: "Can view project, but not make edits or share with others.",
            cls.REVIEWER.name: "Can view project files and leave comments, but not edit project or share with others.",
            cls.EDITOR.name: "Can edit project files and leave comments, but not share with other.",
            cls.AUTHOR.name: "Can edit project files and leave comments, but not share with other.",
            cls.MANAGER.name: "Can edit project files, settings, and share with others.",
            cls.OWNER.name: "Can edit project files, settings, share with others, as well as delete a project",
        }[role.name]

    @classmethod
    def from_string(cls, role: str) -> "ProjectRole":
        """Get the role from a string."""
        role = role.lower()
        for r in cls:
            if role == r.name.lower():
                return r
        raise ValueError('No project role matching "{}"'.format(role))

    @classmethod
    def and_above(cls, role: "ProjectRole") -> List["ProjectRole"]:
        """Get a list including the role and all the roles above it."""
        roles: List["ProjectRole"] = []
        for r in cls:
            if r == role or len(roles) > 0:
                roles.append(r)
        return roles


class ProjectAgent(models.Model):
    """
    A user or team.

    Users or teams can be added, with a role, to a project.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="agents",
        help_text="Project to which the user or team is being given access to.",
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="projects",
        help_text="A user given access to the project.",
    )

    team = models.ForeignKey(
        AccountTeam,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="projects",
        help_text="A team given access to the project.",
    )

    role = models.CharField(
        null=False,
        blank=False,
        max_length=32,
        choices=ProjectRole.as_choices(),
        help_text="Role the user or team has within the project.",
    )

    class Meta:
        constraints = [
            # Each user should only have one role for a project
            models.UniqueConstraint(
                fields=["project", "user"], name="%(class)s_unique_project_user"
            ),
            # Each team should only have one role for a project
            models.UniqueConstraint(
                fields=["project", "team"], name="%(class)s_unique_project_team"
            ),
        ]


class ProjectEvent(models.Model):
    """
    A project event.

    Project events are recorded primarily to provide traceability.
    There are no fixed event types and arbitrary JSON data can be stored
    in the `data` field. Events may be associated with a `source` or a `user`.
    """

    id = models.BigAutoField(primary_key=True, help_text="Id of the event.",)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="events",
        help_text="Project to which the event applies.",
    )

    time = models.DateTimeField(auto_now_add=True, help_text="Time of the event.")

    data = models.JSONField(help_text="Data associated with the event.")

    source = models.ForeignKey(
        "Source",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
        help_text="Source associated with the event.",
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
        help_text="User associated with the event.",
    )
