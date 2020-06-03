from django.db import models

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

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="personal_account",
        help_text="The user for this account. Only applies to personal accounts.",
    )

    name = models.SlugField(
        null=False, blank=False, unique=True, help_text="Name of the account.",
    )

    image = models.ImageField(
        null=True, blank=True, help_text="Image for the account.",
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
