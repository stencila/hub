from knox.models import AuthToken
from rest_framework import serializers

from accounts.models import AccountUserRole
from avatar.utils import get_primary_avatar
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    A serializer for public user details.

    Only fields considered public should be available here.
    """

    avatar = serializers.SerializerMethodField(
        help_text="Path to the user's primary avatar (`null` if the user has no avatar)."
    )

    def get_avatar(self, user):
        avatar = get_primary_avatar(user)
        return avatar.avatar_url(80) if avatar else None

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "avatar"]


class MeSerializer(UserSerializer):
    """
    A serializer for a user's own details.

    Add fields that are private to the user.
    """

    accounts = serializers.SerializerMethodField(
        help_text="Accounts the user is linked to and their role for each."
    )

    def get_accounts(self, user):
        return [
            {"id": aur.account.id, "name": aur.account.name, "role": aur.role.name}
            for aur in AccountUserRole.objects.filter(user=user).prefetch_related(
                "account", "role"
            )
        ]

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ["accounts"]


class TokenSerializer(serializers.ModelSerializer):

    id = serializers.CharField(
        source="token_key", help_text="First eight characters of the token."
    )

    class Meta:
        model = AuthToken
        fields = ["user", "id", "created", "expiry"]
