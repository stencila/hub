"""
Models implementing Stencila Hub `Accounts`.

Against which the usage of the computational resources is metered.
"""

import typing

import djstripe.models
from django.contrib.auth.models import AbstractUser
from django.db import models, IntegrityError
from django.db.models import QuerySet
from django.db.models.signals import post_save
from django.utils.text import slugify

from lib.data_cleaning import clean_slug, SlugType
from lib.enum_choice import EnumChoice

from users.models import User


class AccountPermissionType(EnumChoice):
    """
    Types of account permissions.

    - `VIEW`:       allows read-only access to the account

    - `MODIFY`:     allows write access to some of aspects of the
                    account e.g. creating a new project linked to the account

    - `ADMINISTER`: allows management of teams (create and alter membership),
                    delete account; update billing details, give other members
                    admin role etc.
    """

    VIEW = "view"
    MODIFY = "modify"
    ADMINISTER = "administer"


class AccountPermission(models.Model):
    """
    Model implementing `AccountPermissionType`s.

    It is necessary to have this as a database model because an
    `AccountRole` can have multiple permissions.
    """

    type = models.TextField(
        null=False,
        blank=False,
        choices=AccountPermissionType.as_choices(),
        unique=True,
        help_text="An account permission type.",
    )

    def __str__(self) -> str:
        return self.type


class Account(models.Model):
    """
    Account model.

    Accounts are the entity against which resource usage is metered.
    Every user has their own personal account.
    Organisations can create accounts.
    """

    name = models.SlugField(
        null=False,
        blank=False,
        unique=True,
        help_text="Name of the organisation. Must be unique.",
    )

    logo = models.ImageField(
        null=True,
        blank=True,
        help_text="Logo for the organisation. Please use an image that is 100 x 100 px or smaller.",
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
        help_text="A space separated list of valid hosts for the account."
        "Used for setting Content Security Policy headers when serving content for this account.",
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="account_user",
        help_text="When set, this is the user assigned to a 'personal' account.",
    )

    def save(self, *args, **kwargs) -> None:
        self.name = clean_slug(self.name, SlugType.ACCOUNT)

        super(Account, self).save(*args, **kwargs)

    def get_administrators(self) -> typing.Iterable[User]:
        """Return users who have administrative permissions on the account."""
        ownership_roles: typing.Set[
            AccountUserRole
        ] = set()  # cache the roles that have ownership perms
        users: typing.Set[AbstractUser] = set()

        for user_role in self.user_roles.all():
            user_has_role = False

            if user_role.role.pk in ownership_roles:
                user_has_role = True
            elif AccountPermissionType.ADMINISTER in user_role.role.permissions_types():
                ownership_roles.add(user_role.role.pk)
                user_has_role = True

            if user_has_role:
                users.add(user_role.user)

        return users

    def __str__(self) -> str:
        return self.name

    @property
    def plan(self) -> typing.Union[djstripe.models.Plan, dict]:
        subscription = self.subscriptions.filter(subscription__status="active").first()

        if subscription is None:
            from accounts.static_product_config import FREE_PLAN

            return FREE_PLAN

        return subscription.subscription.plan

    @property
    def is_personal(self) -> bool:
        """Check for personal account type."""
        return self.user is not None


class Team(models.Model):
    """
    Team model.

    Team is can be formed by one or more Users.
    Each User can be a member of multiple Teams.
    Each Team is linked to exactly one Account.
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text="Account to which the Team is linked to. Each Team can be linked to only one account.",
        related_name="teams",
    )

    name = models.TextField(blank=False, null=False, help_text="Name of the team")

    description = models.TextField(blank=True, null=True, help_text="Team description")

    members = models.ManyToManyField(
        "auth.User",
        help_text="Team members. Each User can be a member of multiple Teams.",
    )

    def __str__(self) -> str:
        return self.name


class AccountRole(models.Model):
    """Roles linked to the Organisation, depending on their `AccountPermissionType`."""

    name = models.TextField(
        null=False, blank=False, help_text="The name of the role e.g 'admin'",
    )

    permissions = models.ManyToManyField(
        AccountPermission,
        related_name="roles",
        help_text="One or more permissions that the role has e.g `ADMINISTER`.",
    )

    def permissions_text(self) -> typing.Set[str]:
        return {permission.type for permission in self.permissions.all()}

    def permissions_types(self) -> typing.Set[AccountPermissionType]:
        return set(map(lambda p: AccountPermissionType(p), self.permissions_text()))

    @classmethod
    def roles_with_permission(cls, permission_type: AccountPermissionType) -> QuerySet:
        """Query for a list of `AccountRoles` that have the given permission_type `AccountPermissionType`."""
        # TODO: This is a good candidate for a long cache
        permission = AccountPermission.objects.get(type=permission_type.value)
        return cls.objects.filter(permissions=permission)

    def __str__(self) -> str:
        return self.name


class AccountUserRole(models.Model):
    """Model connecting `Users` with their `Roles` in the `Accounts`."""

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=False,
        related_name="account_roles",
        db_index=True,
    )

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="user_roles", db_index=True
    )

    role = models.ForeignKey(AccountRole, on_delete=models.CASCADE, related_name="+")

    class Meta:
        unique_together = (("user", "account"),)


class AccountSubscription(models.Model):
    """
    Basically just add a "subscriptions" attribute to the Account.

    Ideally you'd just add an "account" attribute to `Subscription` but since we don't have control of that object we do
    it with this extra model. This is why `subscription` is a OneToOneField.
    """

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="subscriptions", db_index=True
    )

    subscription = models.OneToOneField(
        djstripe.models.Subscription, on_delete=models.PROTECT, related_name="account"
    )


class ProductExtension(models.Model):
    """Add extra properties to a `Product` since we don't have control of that model."""

    product = models.OneToOneField(
        djstripe.models.Product, on_delete=models.PROTECT, related_name="extension"
    )
    allowances = models.TextField(
        help_text="Allowances granted in JSON format."
    )  # Another contender for JSONField
    tag_line = models.TextField(help_text="A short tag line for the product.")
    is_purchasable = models.BooleanField(
        null=False,
        default=True,
        help_text="Can this Produce be purchased, False means only can be bought with "
        "a coupon.",
    )


def create_personal_account_for_user(sender, instance, created, *args, **kwargs):
    """
    Create a personal account for a user.

    Called when a new `User` is created and saved.
    Makes sure each user has a Personal `Account` that they are an `admin` on so that their `Projects` can be
    linked to an `Account`.
    """
    if sender is User and created:
        suffix_number = 2
        suffix = ""
        while True:
            if suffix_number == 100:
                raise RuntimeError("Suffix number hit 100.")

            account_name = "{}".format(slugify(instance.username))[:50]

            if suffix:
                account_name = "{}".format(suffix)[:50]

            account_name = "admin-user" if account_name == "admin" else account_name

            try:
                account = Account.objects.create(name=account_name)
                break
            except IntegrityError:
                suffix = "-{}".format(suffix_number)
                suffix_number += 1

        account.user = instance
        account.save()
        admin_role = AccountRole.objects.get(name="admin")
        AccountUserRole.objects.create(role=admin_role, account=account, user=instance)


post_save.connect(create_personal_account_for_user, sender=User)
