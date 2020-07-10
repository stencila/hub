from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from rest_framework import exceptions, viewsets

from accounts.models import Account, AccountRole, AccountTeam
from manager.api.helpers import HtmxCreateMixin, HtmxDestroyMixin, HtmxListMixin
from projects.models.projects import Project, ProjectRole
from users.api.serializers import InviteSerializer
from users.models import Invite


class InvitesViewSet(
    HtmxListMixin, HtmxCreateMixin, HtmxDestroyMixin, viewsets.GenericViewSet,
):
    """
    A view set for invites.

    Provides for `list`, `create` and `destroy` actions.
    Requires authentication because all actions are restricted
    to the `inviter` of the invite instance.
    """

    model = Invite
    queryset_name = "invites"
    object_name = "invite"

    def get_queryset(self) -> QuerySet:
        """
        Get all invites sent by the current user.
        """
        return Invite.objects.filter(inviter=self.request.user).order_by("-created")

    def get_serializer_class(self):
        """
        Get the serializer class for the current action.
        """
        return None if self.action == "destroy" else InviteSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Override to prepare action related fields based on value of others.
        """
        data = self.request.data
        action = data.get("action")
        arguments = dict(
            [
                (key, value)
                for key, value in data.items()
                if key not in ["email", "message", "action"]
            ]
        )

        if action == "join_account":
            if "account" not in arguments:
                raise exceptions.ValidationError(
                    dict(account="Account id is required.")
                )
            if "role" not in arguments:
                arguments.update(role="MEMBER")

            subject_type = ContentType.objects.get_for_model(Account).pk
            subject_id = arguments["account"]
        elif action == "join_team":
            if "team" not in arguments:
                raise exceptions.ValidationError(dict(team="Team id is required."))

            subject_type = ContentType.objects.get_for_model(AccountTeam).pk
            subject_id = arguments["team"]
        elif action == "join_project":
            if "account" not in arguments:
                raise exceptions.ValidationError(
                    dict(account="Account id is required.")
                )
            if "project" not in arguments:
                raise exceptions.ValidationError(
                    dict(project="Project id is required.")
                )
            if "role" not in arguments:
                arguments.update(role="AUTHOR")

            subject_type = ContentType.objects.get_for_model(Project).pk
            subject_id = arguments["project"]
        else:
            subject_type = None
            subject_id = None

        data["arguments"] = arguments
        data["subject_type"] = subject_type
        data["subject_id"] = subject_id

        serializer_class = self.get_serializer_class()
        kwargs["data"] = data
        return serializer_class(*args, **kwargs, context=self.get_serializer_context())

    def get_response_context(self, *args, **kwargs):
        """
        Add a list of possible account and project roles to the template context.
        """
        return super().get_response_context(
            *args,
            **kwargs,
            account_roles=[(e.name, e.value) for e in AccountRole],
            project_roles=[(e.name, e.value) for e in ProjectRole]
        )
