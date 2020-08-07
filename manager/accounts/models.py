import secrets
from typing import Dict

import customidenticon
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.shortcuts import reverse
from imagefield.fields import ImageField

from manager.helpers import EnumChoice, unique_slugify
from manager.storage import media_storage
from users.models import User


class Account(models.Model):
    """
    An account for a user or organization.

    A personal account has a `user`, an organizational account does not.
    """

    tier = models.ForeignKey(
        "AccountTier",
        default=1,
        on_delete=models.DO_NOTHING,
        help_text="The tier of the account. Determines its quota limits.",
    )

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
        null=False,
        blank=False,
        unique=True,
        max_length=64,
        help_text="Name of the account. Lowercase and no spaces or leading numbers. "
        "Will be used in URLS e.g. https://hub.stenci.la/awesome-org",
    )

    image = ImageField(
        null=True,
        blank=True,
        storage=media_storage(),
        upload_to="accounts/images",
        formats={
            "small": ["default", ("crop", (20, 20))],
            "medium": ["default", ("crop", (50, 50))],
            "large": ["default", ("crop", (250, 250))],
        },
        auto_add_fields=True,
        help_text="Image for the account.",
    )

    display_name = models.CharField(
        null=True,
        blank=True,
        max_length=256,
        help_text="Name to display in account profile.",
    )

    location = models.CharField(
        null=True,
        blank=True,
        max_length=256,
        help_text="Location to display in account profile.",
    )

    website = models.URLField(
        null=True, blank=True, help_text="URL to display in account profile.",
    )

    email = models.EmailField(
        null=True,
        blank=True,
        help_text="An email to display in account profile. Will not be used by Stencila to contact you.",
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

    def __str__(self):
        """
        Get the string representation of the account.

        Example of where this is used: to generate the <select>
        <option> display text when choosing an account.
        """
        return self.name

    @property
    def is_personal(self):
        """Is this a personal account."""
        return self.user_id is not None

    @property
    def is_organization(self):
        """Is this an organizational account."""
        return self.user_id is None

    def get_url(self):
        """Get the URL for this account."""
        return reverse("ui-accounts-retrieve", args=[self.name])

    def save(self, *args, **kwargs):
        """
        Save this account.

        - Ensure that name is unique
        - If the account `is_personal` then make sure that the
          user's `username` is the same as `name`
        - Create an image if the account does not have one
        """
        self.name = unique_slugify(self.name, instance=self)

        if self.is_personal and self.user.username != self.name:
            self.user.username = self.name
            self.user.save()

        if not self.image:
            file = ContentFile(customidenticon.create(self.name, size=5))
            # Use a random name because self.pk may not be available
            file.name = secrets.token_hex(12)
            self.image = file

        return super().save(*args, **kwargs)

    # Methods to get "built-in" accounts
    # Optimized for frequent access by use of caching.

    @classmethod
    def get_stencila_account(cls) -> "Account":
        """
        Get the Stencila account object.
        """
        if not hasattr(cls, "_stencila_account"):
            cls._stencila_account = Account.objects.get(name="stencila")
        return cls._stencila_account

    @classmethod
    def get_temp_account(cls) -> "Account":
        """
        Get the 'temp' account object.

        This account owns all temporary projects.
        For compatability with templates and URL resolution
        it is easier and safer to use this temporary account
        than it is to allow `project.account` to be null.
        """
        if not hasattr(cls, "_temp_account"):
            cls._temp_account = Account.objects.get(name="temp")
        return cls._temp_account


def make_account_creator_an_owner(
    sender, instance: Account, created: bool, *args, **kwargs
):
    """
    Make the account create an owner.

    Makes sure each account has at least one owner.
    """
    if sender is Account and created and instance.creator:
        AccountUser.objects.create(
            account=instance, user=instance.creator, role=AccountRole.OWNER.name
        )


post_save.connect(make_account_creator_an_owner, sender=Account)


def create_personal_account_for_user(
    sender, instance: User, created: bool, *args, **kwargs
):
    """
    Create a personal account for a user.

    Makes sure each user has a personal `Account`.
    """
    if sender is User and created:
        Account.objects.create(
            name=instance.username,
            display_name=(
                (instance.first_name or "") + " " + (instance.last_name or "")
            ).strip(),
            creator=instance,
            user=instance,
        )


post_save.connect(create_personal_account_for_user, sender=User)


class AccountTier(models.Model):
    """
    An account tier.

    All accounts belong to a tier.
    The tier determines the quotas for the account.

    Some of the limits are primarily an anti-spamming
    measure e.g.`orgs-created`.
    """

    name = models.CharField(
        null=False,
        blank=False,
        max_length=64,
        unique=True,
        help_text="The name of the tier.",
    )

    active = models.BooleanField(
        default=True, help_text="Is the tier active i.e. should be displayed to users."
    )

    orgs_created = models.IntegerField(
        verbose_name="Organizations created",
        default=10,
        help_text="The maximum number organizations that a user can create.",
    )

    account_users = models.IntegerField(
        verbose_name="Users",
        default=100,
        help_text="The maximum number of users that can be added to the account.",
    )

    account_teams = models.IntegerField(
        verbose_name="Teams",
        default=5,
        help_text="The maximum number of teams that can be added to the account.",
    )

    projects_public = models.IntegerField(
        verbose_name="Public projects",
        default=100,
        help_text="The maximum number of public projects that an account can have.",
    )

    projects_private = models.IntegerField(
        verbose_name="Private projects",
        default=10,
        help_text="The maximum number of private projects that an account can have.",
    )

    storage_working = models.FloatField(
        verbose_name="Working storage",
        default=1,
        help_text="The maximum storage in project working directories (GB).",
    )

    storage_snapshots = models.FloatField(
        verbose_name="Snapshot storage",
        default=5,
        help_text="The maximum storage in project snapshots (GB).",
    )

    file_downloads_month = models.FloatField(
        verbose_name="File downloads",
        default=10,
        help_text="The maximum total size of downloads of project files per month (GB).",
    )

    job_runtime_month = models.FloatField(
        verbose_name="Job minutes",
        default=1000,
        help_text="The maximum number of job minutes per month.",
    )

    def __str__(self) -> str:
        return "Tier {0}".format(self.id)

    @staticmethod
    def fields() -> Dict[str, models.Field]:
        """
        Get a dictionary of fields of an AccountTier.
        """
        return dict(
            (field.name, field)
            for field in AccountTier._meta.get_fields()
            if field.name not in ["id"]
        )


class AccountRole(EnumChoice):
    """
    A user role within an account.

    See `get_description` for what each role can do.
    """

    MEMBER = "Member"
    MANAGER = "Manager"
    OWNER = "Owner"

    @classmethod
    def get_description(cls, role: "AccountRole"):
        """Get the description of an account role."""
        return {
            cls.MEMBER.name: "Can create, update and delete projects.",
            cls.MANAGER.name: "As for member and can create, update and delete teams.",
            cls.OWNER.name: "As for manager and can also add and remove users and change their role.",
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
            models.UniqueConstraint(
                fields=["account", "user"], name="%(class)s_unique_account_user"
            )
        ]


class AccountTeam(models.Model):
    """
    A team within an account.

    Each `AccountTeam` belongs to exactly one `Account`.
    Each `AccountTeam` has one or more `User`s.
    `User`s can be a member of multiple `AccountTeam`s.
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
            models.UniqueConstraint(
                fields=["account", "name"], name="%(class)s_unique_account_name"
            )
        ]

    def save(self, *args, **kwargs):
        """
        Save this team.

        Ensures that name is unique within the account.
        """
        self.name = unique_slugify(
            self.name,
            instance=self,
            queryset=AccountTeam.objects.filter(account=self.account),
        )
        return super().save(*args, **kwargs)
