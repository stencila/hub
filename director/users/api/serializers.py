from avatar.utils import get_primary_avatar
from knox.models import AuthToken
from rest_framework import serializers

from accounts.models import AccountUserRole
from users.models import User


class UserSerializer(serializers.ModelSerializer):

    accounts = serializers.SerializerMethodField(
        help_text="Accounts the user is linked to and their role for each."
    )

    avatar = serializers.SerializerMethodField(
        help_text="Path to the user's primary avatar (`null` if the user has no avatar)."
    )

    def get_accounts(self, user):
        return [
            {"id": aur.account.id, "role": aur.role.name}
            for aur in AccountUserRole.objects.filter(user=self.context["request"].user)
        ]

    def get_avatar(self, user):
        avatar = get_primary_avatar(user)
        return avatar.avatar_url(80) if avatar else None

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "avatar", "accounts"]


class TokenSerializer(serializers.ModelSerializer):

    id = serializers.CharField(
        source="token_key", help_text="First eight characters of the token."
    )

    class Meta:
        model = AuthToken
        fields = ["user", "id", "created", "expiry"]
