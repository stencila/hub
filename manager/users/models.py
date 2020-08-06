"""
Define models used in this app.

This module only serves to provide some consistency across the
`users`, `accounts` , `projects` etc apps so that you can
`from users.models import Users`, just like you can for
`from projects.models import Projects` and instead of having to remember
to do the following.
"""

from typing import Optional

import django.contrib.auth.models
import shortuuid
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpRequest
from django.shortcuts import reverse
from django.utils import timezone
from invitations.adapters import get_invitations_adapter
from invitations.models import Invitation
from jsonfallback.fields import FallbackJSONField
from rest_framework.exceptions import ValidationError
from waffle.models import AbstractUserFlag

# Needed to ensure signals are loaded
import users.signals  # noqa

User: django.contrib.auth.models.User = get_user_model()


def generate_anonuser_id():
    """
    Generate a unique id for an anonymous user.
    """
    return shortuuid.ShortUUID().random(length=32)


class AnonUser(models.Model):
    """
    A model to store anonymous users when necessary.

    Used to associate unauthenticated users with objects,
    for example, so that the same session job can be provided
    to them on multiple page refreshes.
    """

    id = models.CharField(
        primary_key=True,
        max_length=64,
        default=generate_anonuser_id,
        help_text="The unique id of the anonymous user.",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="The time the anon user was created."
    )

    @staticmethod
    def get_id(request: HttpRequest) -> Optional[str]:
        """
        Get the id of the anonymous user, if any.
        """
        if request.user.is_anonymous:
            return request.session.get("user", {}).get("id")
        return None

    @staticmethod
    def get_or_create(request: HttpRequest) -> "AnonUser":
        """
        Create an instance in the database.

        Only use this when necessary. e.g when you need
        to associated an anonymous user with another object.
        """
        id = AnonUser.get_id(request)
        if id:
            anon_user, created = AnonUser.objects.get_or_create(id=id)
            return anon_user
        else:
            anon_user = AnonUser.objects.create()
            request.session["user"] = {"anon": True, "id": anon_user.id}
            return anon_user


class Flag(AbstractUserFlag):
    """
    Custom feature flag model.

    It is only possible to set this custom model once. In the future, fields may be
    added to allow flags to be set based on the account (in addition to, or instead
    of only the user).
    See https://waffle.readthedocs.io/en/stable/types/flag.html#custom-flag-models
    """

    pass


def generate_invite_key():
    """
    Generate a unique invite key.

    The is separate function to avoid new AlterField migrations
    being created as happens when `default=shortuuid.uuid`.
    """
    return shortuuid.ShortUUID().random(length=32)


class Invite(models.Model):
    """
    An extension of the default invitation model.

    Allows for different types of invitations, with actions
    after success.

    Re-implements the interface of `invitations.Invitation`
    instead of extending it so that some fields can be redefined
    e.g shorter case sensitive `key`; e.g. avoid the unique constraint
    on `email` (because of actions, a single email address could
    be invited more than once).

    The methods for each action should use API view sets
    with synthetic requests having the `inviter` as the
    request user. This reduces code and provides consistency
    in permissions checking, thereby reducing errors.

    Adds `subject_object` `GenericForeignKey` to allow
    querying from other models
    """

    key = models.CharField(
        max_length=64,
        unique=True,
        default=generate_invite_key,
        help_text="The key for the invite.",
    )

    inviter = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="invites",
        help_text="The user who created the invite.",
    )

    email = models.EmailField(
        max_length=2048, help_text="The email address of the person you are inviting."
    )

    message = models.TextField(
        null=True, blank=True, help_text="An optional message to send to the invitee."
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="When the invite was created."
    )

    sent = models.DateTimeField(
        null=True, blank=True, help_text="When the invite was sent."
    )

    accepted = models.BooleanField(
        default=False,
        help_text="Whether the invite has been accepted. "
        "Will only be true if the user has clicked on the invitation AND authenticated.",
    )

    completed = models.DateTimeField(
        null=True, blank=True, help_text="When the invite action was completed",
    )

    action = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        choices=[
            ("join_account", "Join account"),
            ("join_team", "Join team"),
            ("join_project", "Join project"),
            ("take_tour", "Take tour"),
        ],
        help_text="The action to perform when the invitee signs up.",
    )

    subject_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="The type of the target of the action. e.g Team, Account",
    )

    subject_id = models.IntegerField(
        null=True, blank=True, help_text="The id of the target of the action.",
    )

    subject_object = GenericForeignKey("subject_type", "subject_id")

    arguments = FallbackJSONField(
        null=True,
        blank=True,
        help_text="Any additional arguments to pass to the action.",
    )

    # These methods need to be implemented for the `invitations` API

    key_expired = Invitation.key_expired

    def send_invitation(self, request):
        """Extend method to add the invite object to the template context."""
        context = dict(
            inviter=self.inviter,
            inviter_name=self.inviter.get_full_name() or self.inviter.username,
            invite_message=self.message,
            invite_url=request.build_absolute_uri(
                reverse("ui-users-invites-accept", args=[self.key])
            ),
            reason_for_sending="This email was sent by user '{0}' to invite you to "
            "collaborate with them on Stencila Hub.".format(self.inviter.username),
        )
        get_invitations_adapter().send_mail(
            "invitations/email/email_invite", self.email, context
        )
        self.sent = timezone.now()
        self.save()

    def __str__(self):
        return "Invite {0} {1}".format(self.action, self.email)

    # These methods implement invitation actions

    def redirect_url(self) -> str:
        """
        Get the URL to redirect the user to after the invite has been accepted.
        """
        if self.action == "join_account":
            return reverse("ui-accounts-retrieve", args=[self.arguments["account"]])
        elif self.action == "join_team":
            return reverse(
                "ui-accounts-teams-retrieve",
                args=[self.arguments["account"], self.arguments["team"]],
            )
        elif self.action == "join_project":
            return reverse(
                "ui-projects-retrieve",
                args=[self.arguments["account"], self.arguments["project"]],
            )
        elif self.action == "take_tour":
            return self.arguments["page"] + "?tour=" + self.arguments["tour"]
        else:
            return "/"

    def create_request(self, data) -> HttpRequest:
        """
        Create a synthetic request to pass to view sets.
        """
        request = HttpRequest()
        request.data = data
        request.user = self.inviter
        return request

    def perform_action(self, request, user=None):
        """
        Perform the action (if any) registered for this invitation.
        """
        # Accept and save in case the action fails below
        self.accepted = True
        self.save()

        if self.action:
            method = getattr(self, self.action)
            if not method:
                raise RuntimeError("No such action {0}".format(self.action))

            method(user or request.user)

        self.completed = timezone.now()
        self.save()

    def join_account(self, invitee):
        """
        Add invitee to account with a particular role.
        """
        from accounts.api.views import AccountsUsersViewSet

        self.arguments["id"] = invitee.id

        request = self.create_request(data=self.arguments)
        viewset = AccountsUsersViewSet.init(
            "create", request, args=[], kwargs=self.arguments
        )
        viewset.create(request, **self.arguments)

    def join_project(self, invitee):
        """
        Add invitee to project with a particular role.

        If the user already has a project role, then the
        invite is ignored.
        """
        from projects.api.views.projects import ProjectsAgentsViewSet

        self.arguments["type"] = "user"
        self.arguments["agent"] = invitee.id

        request = self.create_request(data=self.arguments)
        viewset = ProjectsAgentsViewSet.init(
            "create", request, args=[], kwargs=self.arguments
        )
        try:
            viewset.create(request, **self.arguments)
        except ValidationError as exc:
            if "Already has a project role" not in str(exc):
                raise exc

    def take_tour(self, invitee):
        """
        Nothing needs to be done here. User is redirected to tour URL.
        """
        pass
