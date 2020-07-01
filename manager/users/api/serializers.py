from django.db.models import Q
from django.urls import reverse
from django.utils.crypto import get_random_string
from knox.models import AuthToken
from rest_framework import serializers

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

    def get_url(self, obj):
        """Get the complete URL for the invite."""
        request = self.context["request"]
        return request.build_absolute_uri(
            reverse("ui-users-invites-accept", args=[obj.key])
        )

    class Meta:
        model = Invite
        fields = "__all__"
        read_only_fields = ["key"]

    def create(self, data):
        """Create and send the invite."""
        request = self.context["request"]
        arguments = dict(
            [
                (key, value)
                for key, value in request.data.items()
                if key not in ["email", "message", "action"]
            ]
        )
        invite = Invite.objects.create(
            key=get_random_string(64).lower(),
            inviter=request.user,
            email=data["email"],
            message=data.get("message"),
            action=data.get("action"),
            arguments=arguments,
        )
        invite.send_invitation(request)
        return invite
