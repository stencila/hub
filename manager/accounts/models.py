import secrets

import customidenticon
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from imagefield.fields import ImageField

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
        null=True, auto_now_add=True, help_text="The time the account was created."
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
        """Override to create an image if the account does not have one."""
        if not self.image:
            file = ContentFile(customidenticon.create(self.name, size=5))
            # Use a random name because self.id is not yet available
            file.name = secrets.token_hex(12)
            self.image = file
        return super().save(*args, **kwargs)


def create_personal_account_for_user(sender, instance, created, *args, **kwargs):
    """
    Create a personal account for a user.

    Called when a new `User` is created and saved.
    Makes sure each user has a Personal `Account` that they are an `admin` on.
    """
    if sender is User and created:
        Account.objects.create(name=instance.username, user=instance)


post_save.connect(create_personal_account_for_user, sender=User)


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

    name = models.TextField(blank=False, null=False, help_text="Name of the team.")

    description = models.TextField(blank=True, null=True, help_text="Team description.")

    members = models.ManyToManyField(User, help_text="Team members.")
