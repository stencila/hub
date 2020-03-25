import knox.models
from rest_framework import serializers


class TokenSerializer(serializers.ModelSerializer):

    id = serializers.CharField(
        source="token_key", help_text="First eight characters of the token."
    )

    class Meta:
        model = knox.models.AuthToken
        fields = ["user", "id", "created", "expiry"]
