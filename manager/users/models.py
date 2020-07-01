"""
Define models used in this app.

This module only serves to provide some consistency across the
`users`, `accounts` , `projects` etc apps so that you can
`from users.models import Users`, just like you can for
`from projects.models import Projects` and instead of having to remember
to do the following.
"""

import invitations
from django.contrib.auth import get_user_model
from django.db import models
from django.http import HttpRequest
from django.shortcuts import reverse
from jsonfallback.fields import FallbackJSONField

User = get_user_model()


class Invite(invitations.models.AbstractBaseInvitation):
    """
    An extension of the default invitation model.

    Allows for different types of invitations, with actions
    after success.

    Overrides the `email` field to remove the unique constraint
    (because of actions, a single email address could be invited
    more than once).

    The methods for each action should use API view sets
    with synthetic requests having the `inviter` as the
    request user. This reduces code and provides consistency
    in permissions checking, thereby reducing errors.
    """

    email = models.EmailField(
        max_length=2048, help_text="The email address of the invitee."
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="When the invite was created."
    )

    created = models.BooleanField(
        default=False,
        help_text="Whether or not the invitation action have been completed",
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

    arguments = FallbackJSONField(
        null=True, blank=True, help_text="Arguments to pass to the action."
    )

    message = models.TextField(
        null=True, blank=True, help_text="An optional message to send to the invitee."
    )

    # These methods need to be implemented
    key_expired = invitations.models.Invitation.key_expired
    send_invitation = invitations.models.Invitation.send_invitation

    def __str__(self):
        return "Invite {0} {1}".format(self.action, self.email)

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
        if not self.action:
            return

        method = getattr(self, self.action)
        if not method:
            raise RuntimeError("No such action {0}".format(self.action))

        method(user or request.user)

        self.completed = True
        self.save()

    def join_account(self, invitee):
        """
        Add invitee to account with a particular role.
        """
        assert "account" in self.arguments
        self.arguments["id"] = invitee.id
        if "role" not in self.arguments:
            self.arguments["role"] = "MEMBER"

        from accounts.api.views import AccountsUsersViewSet

        request = self.create_request(data=self.arguments)
        viewset = AccountsUsersViewSet.init(
            "create", request, args=[], kwargs=self.arguments
        )
        viewset.create(request, **self.arguments)

    def take_tour(self, invitee):
        """
        Nothing needs to be done here. User is redirected to tour URL.
        """
        pass
