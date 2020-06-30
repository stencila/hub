from django.db import models
from django.db.models.signals import post_save

from accounts.models import Account, AccountTeam
from jobs.models import Job, JobMethod
from manager.helpers import EnumChoice
from users.models import User


class Project(models.Model):
    """
    A project.

    Projects are always owned by an account.
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="projects",
        null=False,
        blank=False,
        help_text="Account that the project belongs to.",
    )

    creator = models.ForeignKey(
        "auth.User",
        null=True,
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

    public = models.BooleanField(
        default=True, help_text="Should the project be publicly visible?"
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

    main = models.ForeignKey(
        "File",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="project_main",
        help_text="Main file of the project.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["account", "name"], name="%(class)s_unique_account_name"
            )
        ]

    def get_main(self) -> str:
        """
        Get the main file for the project.

        The main file can be designated by the user,
        but if not them defaults to main.* or README.*
        if those are present.
        """
        if self.main:
            return self.main.path
        else:
            # TODO
            return None

    def get_theme(self) -> str:
        """Get the theme for the project."""
        return self.theme or self.account.theme

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
