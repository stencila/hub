"""
Define models used in this app.

This module only serves to provide some consistency across the
`users`, `accounts` , `projects` etc apps so that you can
`from users.models import Users`, just like you can for
`from projects.models import Projects` and instead of having to remember
to do the following.
"""

from typing import Dict, Optional, Union

import django.contrib.auth.models
import shortuuid
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import connection, models
from django.db.models import Count, F, Max, Q
from django.db.models.expressions import RawSQL
from django.http import HttpRequest
from django.shortcuts import reverse
from django.utils import timezone
from invitations.adapters import get_invitations_adapter
from invitations.models import Invitation
from rest_framework.exceptions import ValidationError
from waffle.models import AbstractUserFlag

# Needed to ensure signals are loaded
import users.signals  # noqa
from manager.helpers import EnumChoice

User: django.contrib.auth.models.User = get_user_model()


def get_email(user: User) -> Optional[str]:
    """
    Get the best email address for a user.

    The "best" email is the verified primary email,
    falling back to verified if none marked as primary,
    falling back to the first if none is verified,
    falling back to `user.email`, falling back to
    their public email.
    """
    best = None

    emails = user.emailaddress_set.all()
    for email in emails:
        if (email.primary and email.verified) or (not best and email.verified):
            best = email.email

    if not best and len(emails) > 0:
        best = emails[0].email

    if not best:
        best = user.email

    if not best and user.personal_account:
        best = user.personal_account.email

    # Avoid returning an empty string, return None instead
    return best or None


def get_name(user: User) -> Optional[str]:
    """
    Get the best name to display for a user.

    The "best" name is their account's display name,
    falling back to first_name + last_name,
    falling back to username.
    """
    if user.personal_account and user.personal_account.display_name:
        return user.personal_account.display_name

    if user.first_name or user.last_name:
        return f"{user.first_name} {user.last_name}".strip()

    return user.username


def get_attributes(user: User) -> Dict:
    """
    Get a dictionary of user attributes.

    Used for updating external services with current
    values of user attributes e.g number of projects etc.
    Flattens various other summary dictionaries e.g `get_projects_summary`
    into a single dictionary.
    """
    return {
        **dict(
            (f"feature_{name}", value)
            for name, value in get_feature_flags(user).items()
        ),
        **dict(
            (f"orgs_{name}", value) for name, value in get_orgs_summary(user).items()
        ),
        **dict(
            (f"projects_{name}", value)
            for name, value in get_projects_summary(user).items()
        ),
    }


def get_orgs(user: User):
    """
    Get all organizational accounts that a user is a member of.
    """
    from accounts.models import Account

    return Account.objects.filter(user__isnull=True, users__user=user).annotate(
        role=F("users__role")
    )


def get_orgs_summary(user: User) -> Dict:
    """
    Get a summary of organizational accounts the user is a member of.
    """
    from accounts.models import AccountRole

    zero_by_role = dict([(role.name.lower(), 0) for role in AccountRole])
    orgs = get_orgs(user)
    orgs_summary = orgs.values("role").annotate(count=Count("id"), tier=Max("tier"))
    orgs_by_role = dict([(row["role"].lower(), row["count"]) for row in orgs_summary])
    return {
        "max_tier": max(row["tier"] for row in orgs_summary) if orgs_summary else None,
        "total": sum(orgs_by_role.values()),
        **zero_by_role,
        **orgs_by_role,
    }


def get_projects(user: User, include_public=True):
    """
    Get a queryset of projects for the user.

    For authenticated users, each project is annotated with the
    role of the user for the project.
    """
    from projects.models.projects import Project

    if user.is_authenticated:
        # Annotate the queryset with the role of the user
        # Role is the "greater" of the project role and the
        # account role (for the account that owns the project).
        # Authenticated users can see public projects and those in
        # which they have a role
        return Project.objects.annotate(
            role=RawSQL(
                """
SELECT
CASE account_role.role
WHEN 'OWNER' THEN 'OWNER'
WHEN 'MANAGER' THEN
    CASE project_role.role
    WHEN 'OWNER' THEN 'OWNER'
    ELSE 'MANAGER' END
ELSE project_role.role END AS "role"
FROM projects_project AS project
LEFT JOIN
    (SELECT project_id, "role" FROM projects_projectagent WHERE user_id = %s) AS project_role
    ON project.id = project_role.project_id
LEFT JOIN
    (SELECT account_id, "role" FROM accounts_accountuser WHERE user_id = %s) AS account_role
    ON project.account_id = account_role.account_id
WHERE project.id = projects_project.id""",
                [user.id, user.id],
            )
        ).filter((Q(public=True) if include_public else Q()) | Q(role__isnull=False))
    else:
        # Unauthenticated users can only see public projects
        return Project.objects.filter(public=True).extra(select={"role": "NULL"})


def get_projects_summary(user: User) -> Dict:
    """
    Get a summary of project memberships for a user.
    """
    from projects.models.projects import ProjectRole

    zero_by_role = dict([(role.name.lower(), 0) for role in ProjectRole])
    projects = get_projects(user, include_public=False)
    projects_by_role = dict(
        [
            (row["role"].lower(), row["count"])
            for row in projects.values("role").annotate(count=Count("id"))
        ]
    )
    return {
        "total": sum(projects_by_role.values()),
        **zero_by_role,
        **projects_by_role,
    }


def get_feature_flags(user: User) -> Dict[str, str]:
    """
    Get the feature flag settings for a user.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT "name", "default", "user_id"
            FROM users_flag
            LEFT JOIN (
                SELECT *
                FROM users_flag_users
                WHERE user_id = %s
            ) AS subquery ON users_flag.id = subquery.flag_id
            WHERE users_flag.settable
            """,
            [user.id],
        )
        rows = cursor.fetchall()

    features = {}
    for row in rows:
        name, default, has_flag = row
        if has_flag:
            features[name] = "off" if default == "on" else "on"
        else:
            features[name] = default

    return features


def get_custom_attributes(user: User) -> Dict[str, Union[bool, int, str]]:
    """
    Get a dictionary of custom attributes for the user.

    These are summary attributes of the user, derived from other data,
    that do not fit into one of the other groups e.g. `get_projects_summary`.
    They are added as needed, principally for use in external integrations.
    """
    # User is a member of at least one project that is (a) owned by eLife, or
    # (b) has an eLife source.
    elife_author = (
        get_projects(user, include_public=False)
        .filter(Q(account__name="elife") | Q(sources__address__startswith="elife://"))
        .count()
        > 0
    )

    return dict(elife_author=elife_author)


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

    Adds fields to allow users to turn features on/off themselves.

    In the future, fields may be
    added to allow flags to be set based on the account (in addition to, or instead
    of, only the user).
    See https://waffle.readthedocs.io/en/stable/types/flag.html#custom-flag-models
    """

    label = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="A label for the feature to display to users.",
    )

    default = models.CharField(
        max_length=3,
        choices=[("on", "On"), ("off", "Off")],
        default="on",
        help_text='If the default is "on" then when the flag is active, '
        'the feature should be considered "off" and vice versa.',
    )

    settable = models.BooleanField(
        default=False, help_text="User can turn this flag on/off for themselves."
    )

    def is_active_for_user(self, user) -> bool:
        """
        Is the feature "on" for a user.

        Changes the underlying behaviour of Waffle flags based on
        the `default` field for the flag.
        """
        is_active = super().is_active_for_user(user)
        return is_active if self.default == "off" else not is_active


def generate_invite_key():
    """
    Generate a unique invite key.

    The is separate function to avoid new AlterField migrations
    being created as happens when `default=shortuuid.uuid`.
    """
    return shortuuid.ShortUUID().random(length=32)


class InviteAction(EnumChoice):
    """
    Actions to take when a user has accepted an invite.
    """

    join_account = "join_account"
    join_team = "join_team"
    join_project = "join_project"
    take_tour = "take_tour"

    @staticmethod
    def as_choices():
        """Return as a list of field choices."""
        return [
            (InviteAction.join_account.name, "Join account"),
            (InviteAction.join_team.name, "Join team"),
            (InviteAction.join_project.name, "Join project"),
            (InviteAction.take_tour.name, "Take tour"),
        ]


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
        choices=InviteAction.as_choices(),
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

    arguments = models.JSONField(
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
