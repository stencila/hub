import datetime
from typing import Dict, Optional
from urllib.parse import urlencode

import shortuuid
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.shortcuts import reverse

from accounts.models import Account, AccountTeam
from jobs.models import Job, JobMethod
from manager.helpers import EnumChoice
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
            # ("live", "Use working directory"),
            ("latest", "Use latest snapshot"),
            ("pinned", "Pinned to snapshot"),
        )


def generate_project_key():
    """
    Generate a unique, and very difficult to guess, project key.
    """
    return shortuuid.ShortUUID().random(length=32)


class Project(models.Model):
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

    key = models.CharField(
        default=generate_project_key,
        max_length=64,
        help_text="A unique, and very difficult to guess, key to access this project if it is not public.",
    )

    description = models.TextField(
        null=True, blank=True, help_text="Brief description of the project."
    )

    theme = models.TextField(
        null=True,
        blank=True,
        help_text="The name of the theme to use as the default when generating content for this project."
        # See note for the `Account.theme` field for why this is a TextField.
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

    def __str__(self):
        return self.name

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
                return self.files.get(path=self.main, current=True)
            except ObjectDoesNotExist:
                pass

        candidates = self.files.filter(
            Q(path__startswith="main.") | Q(path__startswith="README.")
        ).order_by("-modified")
        if len(candidates):
            return candidates[0]

        return None

    def get_theme(self) -> str:
        """Get the theme for the project."""
        return self.theme or self.account.theme

    def content_url(self, snapshot=None, path=None) -> str:
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
        if snapshot:
            url += "v{0}/".format(snapshot.number)
        if path:
            url += path
        if not self.public:
            params.update(key=self.key)
        if params:
            url += "?" + urlencode(params)
        return url

    def clean(self, user: User) -> Job:
        """
        Clean the project's working directory.

        Removes all files from the working directory.
        In the future, this may be smarter and only remove
        those files that are orphaned (i.e. not registered as part of the pipeline)
        """
        return Job.objects.create(
            description="Clean project '{0}'".format(self.name),
            project=self,
            creator=user,
            method=JobMethod.clean.name,
            params=dict(project=self.id),
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
