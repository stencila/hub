"""
Models related to providers of project sources.

Most of these models can be though of a helpers
associated with one or more provider of a project source.

For example, they might be used to pre-fetch a list
of possible sources for a user from a particular provider
e.g. a list all the GitHub repos that a user has access to.
"""

import logging
from typing import Optional

import github
from allauth.socialaccount.models import SocialToken
from django.db import models, transaction
from django.utils import timezone
from github import Github

from users.models import User
from users.socialaccount.tokens import Provider, get_user_social_token

logger = logging.getLogger(__name__)


class GithubRepo(models.Model):
    """
    A GitHub repository that a user has access to.

    A list of GitHub repos is maintained for each user that
    has a linked GitHub account. This makes it much faster
    for users to be able to search through a list when adding
    a GitHub source to a project.
    """

    refreshed = models.DateTimeField(
        auto_now=True,
        help_text="The date-time that this information was last refreshed from GitHub.",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user who has access to the repository.",
    )

    full_name = models.CharField(
        max_length=512, help_text="The full name of the repository ie. owner/name",
    )

    image_url = models.URLField(
        help_text="The URL for an image associated with the repository."
    )

    permissions = models.JSONField(
        help_text="A JSON object with permissions that the user has for the repo."
    )

    updated = models.DateTimeField(
        help_text="The date-time that the repository was last updated."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "full_name"], name="%(class)s_unique_user_full_name"
            )
        ]

    @staticmethod
    def refresh_for_all_users():
        """
        Refresh the list of repos for all users with a GitHub token.
        """
        tokens = SocialToken.objects.filter(
            app__provider=Provider.github.name
        ).select_related("account__user")
        for token in tokens:
            try:
                GithubRepo.refresh_for_user(token.account.user, token)
            except Exception as exc:
                logger.warn(str(exc))

    @staticmethod
    @transaction.atomic
    def refresh_for_user(user: User, token: Optional[SocialToken] = None):
        """
        Refresh the list of repos for the user.
        """
        # Get a token for the user
        if not token:
            token = get_user_social_token(user, Provider.github)
            if not token:
                return

        # Get all the repositories the user has explicit permission to access
        # See https://docs.github.com/en/free-pro-team@latest/rest/reference/repos#list-repositories-for-the-authenticated-user   # noqa
        #   "The authenticated user has explicit permission to access repositories
        #   they own, repositories where they are a collaborator, and repositories
        #   that they can access through an organization membership."
        try:
            repos = list(Github(token.token).get_user().get_repos())
        except github.BadCredentialsException:
            logger.warn(f"Bad GitHub credentials for user {user.username}")
            return

        # Remove all repos for the user so we can do `bulk_create`
        GithubRepo.objects.filter(user=user).delete()

        # Bulk create repos for the user
        # Previously we used `update_or_create` for this, but `bulk_create`
        # is much faster, particularly when a user has lots of repos.
        GithubRepo.objects.bulk_create(
            [
                GithubRepo(
                    user=user,
                    full_name=repo.full_name,
                    image_url=repo.owner.avatar_url,
                    permissions=dict(
                        admin=repo.permissions.admin,
                        pull=repo.permissions.pull,
                        push=repo.permissions.push,
                    ),
                    updated=timezone.make_aware(repo.updated_at, timezone=timezone.utc),
                )
                for repo in repos
            ]
        )
