import logging
import os
import re
from typing import Dict, Union

import customidenticon
import djstripe
import httpx
import shortuuid
import stripe
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.shortcuts import reverse
from imagefield.fields import ImageField
from meta.views import Meta

import accounts.webhooks  # noqa
from manager.helpers import EnumChoice, unique_slugify
from manager.storage import media_storage
from users.models import User

logger = logging.getLogger(__name__)

stripe.api_key = (
    settings.STRIPE_LIVE_SECRET_KEY
    if settings.STRIPE_LIVE_MODE
    else settings.STRIPE_TEST_SECRET_KEY
)


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

    customer = models.OneToOneField(
        djstripe.models.Customer,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="account",
        help_text="The Stripe customer instance (if this account has ever been one)",
    )

    billing_email = models.EmailField(
        null=True,
        blank=True,
        help_text="The email to use for billing (e.g. sending invoices)",
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

    extra_head = models.TextField(
        null=True,
        blank=True,
        help_text="Content to inject into the <head> element of HTML served for this account.",
    )

    extra_top = models.TextField(
        null=True,
        blank=True,
        help_text="Content to inject at the top of the <body> element of HTML served for this account.",
    )

    extra_bottom = models.TextField(
        null=True,
        blank=True,
        help_text="Content to inject at the bottom of the <body> element of HTML served for this account.",
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

    def get_meta(self) -> Meta:
        """
        Get the metadata to include in the head of the account's page.
        """
        return Meta(
            object_type="profile",
            extra_custom_props=[
                ("property", "profile.username", self.user.username),
                ("property", "profile.first_name", self.user.first_name),
                ("property", "profile.last_name", self.user.last_name),
            ]
            if self.user
            else [],
            title=self.display_name or self.name,
            image=self.image.large,
        )

    def save(self, *args, **kwargs):
        """
        Save this account.

        - Ensure that name is unique
        - If the account `is_personal` then make sure that the
          user's `username` is the same as `name`
        - If the account `is_customer` then update the Stripe
          `Customer` instance
        - Create an image if the account does not have one
        """
        self.name = unique_slugify(self.name, instance=self)

        if self.is_personal and self.user.username != self.name:
            self.user.username = self.name
            self.user.save()

        if self.is_customer:
            self.update_customer()

        if not self.image:
            self.set_image_from_name(should_save=False)

        return super().save(*args, **kwargs)

    # Methods related to billing of this account

    @property
    def is_customer(self) -> bool:
        """
        Is this account a customer (past or present).
        """
        return self.customer_id is not None

    def get_customer(self) -> djstripe.models.Customer:
        """
        Create a Stripe customer instance for this account (if necessary).

        Creates remote and local instances (instead of waiting for webhook notification).
        """
        if self.customer_id:
            return self.customer

        name = self.display_name or self.name or ""
        email = self.billing_email or self.email or ""

        if stripe.api_key != "sk_test_xxxx":
            try:
                customer = stripe.Customer.create(name=name, email=email)
                self.customer = djstripe.models.Customer.sync_from_stripe_data(customer)
            except Exception:
                logger.exception("Error creating customer on Stripe")
        else:
            self.customer = djstripe.models.Customer.objects.create(
                id=shortuuid.uuid(), name=name, email=email
            )

        self.save()
        return self.customer

    def update_customer(self):
        """
        Update the Stripe customer instance for this account.

        Used when the account changes its name/s or email/s.
        Updates remote and local instances (instead of waiting for webhook notification).
        """
        customer = self.customer
        name = self.display_name or self.name or ""
        email = self.billing_email or self.email or ""

        if stripe.api_key != "sk_test_xxxx":
            try:
                stripe.Customer.modify(customer.id, name=name, email=email)
            except Exception:
                logger.exception("Error syncing customer with Stripe")

        customer.name = name
        customer.email = email
        customer.save()

    def get_customer_portal_session(self, request):
        """
        Create a customer portal session for the account.

        If the customer has no valid subscription then create one
        to the free account (this is necessary for the Stripe Customer Portal to
        work properly e.g. to be able to upgrade subscription).
        """
        customer = self.get_customer()

        has_subscription = False
        for subscription in customer.subscriptions.all():
            if subscription.is_valid():
                has_subscription = True
                break

        if not has_subscription:
            price = AccountTier.free_tier().product.prices.first()
            customer.subscribe(price=price)

        return stripe.billing_portal.Session.create(
            customer=customer.id,
            return_url=request.build_absolute_uri(
                reverse("ui-accounts-plan", kwargs={"account": self.name})
            ),
        )

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

    # Methods for setting the account image in various ways

    def image_is_identicon(self) -> bool:
        """
        Is the account image a default identicon.
        """
        filename = os.path.basename(self.image.name)
        return (
            filename.startswith("identicon")
            or re.match(r"[0-9a-f]{24}\.png", filename) is not None
        )

    def set_image_from_name(self, should_save: bool = False):
        """
        Set the image as an "identicon" based on the account name.

        Prefixes the file name of the image with identicon so that
        we can easily tell if it is a default and should be replaced by
        images that may be available from external accounts e.g. Google.
        """
        file = ContentFile(customidenticon.create(self.name, size=5))
        file.name = "identicon-" + shortuuid.uuid()
        self.image = file
        if should_save:
            self.save()

    def set_image_from_url(self, url: str):
        """
        Set the image from a URL.
        """
        response = httpx.get(url)
        if response.status_code == 200:
            file = ContentFile(response.content)
            file.name = "url-" + shortuuid.uuid()
            self.image = file
            self.save()

    def set_image_from_socialaccount(self, socialaccount: Union[str, SocialAccount]):
        """
        Set the image from a social account if possible.

        Does nothing for organizational accounts (where `self.user` is null).
        """
        if not self.image_is_identicon():
            return

        if not isinstance(socialaccount, SocialAccount):
            try:
                socialaccount = SocialAccount.objects.get(
                    user=self.user, provider=socialaccount
                )
            except SocialAccount.DoesNotExist:
                return

        url = None
        provider = socialaccount.provider
        data = socialaccount.extra_data
        if provider == "google":
            url = data.get("picture")
        elif provider == "github":
            url = data.get("avatar_url")
        elif provider == "twitter":
            url = data.get("profile_image_url")

        if url:
            self.set_image_from_url(url)

    def set_image_from_socialaccounts(self):
        """
        Set the image from any of the account's social accounts if possible.

        Does nothing for organizational accounts (where `self.user` is null)
        or if the image is already not an identicon.
        """
        if not self.image_is_identicon():
            return

        socialaccounts = SocialAccount.objects.filter(user=self.user)
        for socialaccount in socialaccounts:
            self.set_image_from_socialaccount(socialaccount)
            if not self.image_is_identicon():
                return


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

    product = models.OneToOneField(
        djstripe.models.Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="account_tier",
        help_text="The Stripe product for the account tier.",
    )

    summary = models.TextField(
        null=True, help_text="A user facing, summary description of the account tier."
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

    dois_created_month = models.IntegerField(
        verbose_name="DOIs minted",
        default=0,
        help_text="The maximum number of DOIs minted per month.",
    )

    def __str__(self) -> str:
        return "Tier {0}".format(self.id)

    @staticmethod
    def active_tiers():
        """
        Get a list of tiers that are active and have a product.
        """
        return (
            AccountTier.objects.filter(active=True, product__isnull=False)
            .order_by("id")
            .all()
        )

    @staticmethod
    def free_tier():
        """
        Get the free tier.
        """
        return AccountTier.objects.get(id=1)

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

    @property
    def title(self) -> float:
        """
        Get the "title" of the account tier.

        Uses the associated product name, falling back to the tier name.
        """
        return self.product.name if self.product else self.name

    @property
    def price(self) -> float:
        """
        Get the current price the associated product.

        If there is no associated product or price then
        return -1 which equates to "Contact us".
        """
        if self.product:
            price = self.product.prices.filter(active=True).first()
            return int(price.unit_amount / 100)
        return -1


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
