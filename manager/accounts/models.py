import secrets

import customidenticon
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from imagefield.fields import ImageField

from manager.helpers import EnumChoice, unique_slugify
from users.models import User


class Account(models.Model):
    """
    An account for a user or organization.

    A personal account has a `user`, an organizational account does not.
    """

    creator = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="accounts_created",
        help_text="The user who created the account.",
    )

    created = models.DateTimeField(
        null=False, auto_now_add=True, help_text="The time the account was created."
    )

    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        # Cascade delete so that when the user is deleted, so is this account.
        # Avoid using `SET_NULL` here as that could result in a personal
        # account being treated as an organization if the user is deleted.
        on_delete=models.CASCADE,
        related_name="personal_account",
        help_text="The user for this account. Only applies to personal accounts.",
    )

    name = models.SlugField(
        null=False, blank=False, unique=True, help_text="Name of the account.",
    )

    image = ImageField(
        null=True,
        blank=True,
        formats={
            "small": ["default", ("crop", (20, 20))],
            "medium": ["default", ("crop", (50, 50))],
            "large": ["default", ("crop", (250, 250))],
        },
        auto_add_fields=True,
        help_text="Image for the account.",
    )

    theme = models.TextField(
        null=True,
        blank=True,
        help_text="The name of the theme to use as the default when generating content for this account."
        # In the future this may be a path to a Thema compatible theme hosted on the Hub or elsewhere.
        # Because of that, it is not a ChoiceField based on the list of names in `assets.thema.themes`.
    )

    hosts = models.TextField(
        null=True,
        blank=True,
        help_text="A space separated list of valid hosts for the account. "
        "Used for setting Content Security Policy headers when serving content for this account.",
    )

    @property
    def is_personal(self):
        """Is this a personal account."""
        return self.user is not None

    @property
    def is_organization(self):
        """Is this an organizational account."""
        return self.user is None

    def save(self, *args, **kwargs):
        """
        Save this account.

        - Ensure that name is unique
        - Create an image if the account does not have one
        """
        self.name = unique_slugify(self, self.name, slug_field_name="name")

        if not self.image:
            file = ContentFile(customidenticon.create(self.name, size=5))
            # Use a random name because self.pk may not be available
            file.name = secrets.token_hex(12)
            self.image = file

        return super().save(*args, **kwargs)


def make_account_creator_an_administrator(
    sender, instance: Account, created: bool, *args, **kwargs
):
    """
    Make the account create an administrator.

    Makes sure each account has at least one administrator.
    """
    if sender is Account and created and instance.creator:
        AccountUser.objects.create(
            account=instance, user=instance.creator, role=AccountRole.ADMIN.name
        )


post_save.connect(make_account_creator_an_administrator, sender=Account)


def create_personal_account_for_user(
    sender, instance: User, created: bool, *args, **kwargs
):
    """
    Create a personal account for a user.

    Makes sure each user has a personal `Account`.
    """
    if sender is User and created:
        Account.objects.create(name=instance.username, creator=instance, user=instance)


post_save.connect(create_personal_account_for_user, sender=User)


class AccountRole(EnumChoice):
    """
    A user role within an account.

    See `get_description` for what each role can do.
    """

    MEMBER = "Member"
    MANAGER = "Manager"
    ADMIN = "Admin"

    @classmethod
    def get_description(cls, role: "AccountRole"):
        """Get the description of an account role."""
        return {
            cls.MEMBER.name: "Account member: can create and delete projects.",
            cls.MANAGER.name: "Account manager: as for member and can create, update and delete teams.",
            cls.ADMIN.name: "Account administrator: as for manager and can add other users to the account.",
        }[role.name]


class AccountUser(models.Model):
    """
    An account user.

    Users can be added, with a role, to an account.
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text="Account to which the user belongs.",
        related_name="users",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User added to the account.",
        related_name="accounts",
    )

    role = models.CharField(
        null=False,
        blank=False,
        max_length=32,
        choices=AccountRole.as_choices(),
        help_text="Role the user has within the account.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["account", "user"], name="unique_user")
        ]


class Team(models.Model):
    """
    A team within an account.

    Each `Team` belongs to exactly one `Account`.
    Each `Team` has one or more `User`s.
    `User`s can be a member of multiple `Team`s.
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text="Account to which the team belongs.",
        related_name="teams",
    )

    name = models.SlugField(blank=False, null=False, help_text="Name of the team.")

    description = models.TextField(blank=True, null=True, help_text="Team description.")

    members = models.ManyToManyField(User, help_text="Team members.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["account", "name"], name="unique_name")
        ]

    def save(self, *args, **kwargs):
        """
        Save this team.

        Ensures that name is unique within the account.
        """
        self.name = unique_slugify(
            self,
            self.name,
            slug_field_name="name",
            queryset=Team.objects.filter(account=self.account),
        )
        return super().save(*args, **kwargs)
