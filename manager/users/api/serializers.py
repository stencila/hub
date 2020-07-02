from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.urls import reverse
from knox.models import AuthToken
from rest_framework import exceptions, serializers

from accounts.models import Account, AccountTeam
from projects.models.projects import Project
from users.models import Invite, User


class UserSerializer(serializers.ModelSerializer):
    """
    A serializer for public user details.

    Only fields considered public should be available here.
    """

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class UserIdentifierSerializer(serializers.Serializer):
    """
    A serializer for specifying a user.

    Allow client to specify the user using either their
    `id` or `username`. Used for POSTing users to lists
    e.g. team membership
    """

    id = serializers.IntegerField(required=False)

    username = serializers.CharField(required=False)

    class Meta:
        ref_name = None

    def validate(self, data):
        """
        Validate the suppied data.

        Check that either is or username is provided
        and that the user exists.
        """
        if "id" not in data and "username" not in data:
            raise serializers.ValidationError("One of `id` or `username` is required")
        try:
            data["user"] = User.objects.get(
                Q(id=data.get("id")) | Q(username=data.get("username"))
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return data


class MeSerializer(UserSerializer):
    """
    A serializer for a user's own details.

    Adds fields that are private to the user.
    """

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields


class TokenSerializer(serializers.ModelSerializer):
    """
    A serializer for user tokens.

    Renames the `token_key` field to `id`.
    """

    id = serializers.CharField(
        source="token_key", help_text="First eight characters of the token."
    )

    class Meta:
        model = AuthToken
        fields = ["user", "id", "created", "expiry"]


class InviteSerializer(serializers.ModelSerializer):
    """
    A serializer for invites.
    """

    url = serializers.SerializerMethodField()

    class Meta:
        model = Invite
        fields = "__all__"
        read_only_fields = ["key"]

    def get_url(self, obj) -> str:
        """Get the absolute URL for the invite."""
        request = self.context["request"]
        return request.build_absolute_uri(
            reverse("ui-users-invites-accept", args=[obj.key])
        )

    def create(self, data):
        """Create and send the invite."""
        request = self.context["request"]
        action = data.get("action")
        arguments = dict(
            [
                (key, value)
                for key, value in request.data.items()
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

            subject_type = ContentType.objects.get_for_model(Account)
            subject_id = arguments["account"]
        elif action == "join_team":
            if "team" not in arguments:
                raise exceptions.ValidationError(dict(team="Team id is required."))

            subject_type = ContentType.objects.get_for_model(AccountTeam)
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

            subject_type = ContentType.objects.get_for_model(Project)
            subject_id = arguments["project"]
        else:
            subject_type = None
            subject_id = None

        invite = Invite.objects.create(
            inviter=request.user,
            email=data["email"],
            message=data.get("message"),
            action=data.get("action"),
            arguments=arguments,
            subject_type=subject_type,
            subject_id=subject_id,
        )
        invite.send_invitation(request)

        return invite
