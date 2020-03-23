from avatar.utils import get_primary_avatar
from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField(
        help_text="Path to the user's primary avatar (`null` if the user has no avatar)."
    )

    def get_avatar(self, user):
        avatar = get_primary_avatar(user)
        return avatar.avatar_url(80) if avatar else None

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "avatar")
