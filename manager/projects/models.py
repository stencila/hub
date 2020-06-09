from django.db import models

from accounts.models import Account, AccountTeam
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
        default=False, help_text="Should the project be publicly visible?"
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["account", "name"], name="unique_project_name"
            )
        ]


class ProjectRole(EnumChoice):
    """
    A user or team role within an account.

    See `get_description` for what each role can do.
    Some of roles can alos be applied to the public.
    For example, a project might be made public with
    the `COMMENTER` role allowing anyone to comment.
    """

    READER = "Reader"
    COMMENTER = "Commenter"
    SUGGESTER = "Suggester"
    AUTHOR = "Author"
    OWNER = "Owner"

    @classmethod
    def get_description(cls, role: "ProjectRole"):
        """Get the description of a project role."""
        return {
            cls.READER.name: "Project reader",
            cls.COMMENTER.name: "Project commenter",
            cls.SUGGESTER.name: "Project suggester",
            cls.AUTHOR.name: "Project author",
            cls.OWNER.name: "Project owner",
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
        on_delete=models.CASCADE,
        related_name="projects",
        help_text="A user given access to the project.",
    )

    team = models.ForeignKey(
        AccountTeam,
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
            models.UniqueConstraint(
                fields=["project", "user", "team"], name="unique_agent"
            )
        ]
