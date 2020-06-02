from knox.models import AuthToken
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    A serializer for public user details.

    Only fields considered public should be available here.
    """

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


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
