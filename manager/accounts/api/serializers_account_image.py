from rest_framework import serializers

from accounts.models import Account


class AccountImageSerializer(serializers.Serializer):
    """
    A serializer for account images.

    The main purpose of this class is to provide a subschema
    for the type of the account.image in responses.
    """

    small = serializers.CharField()
    medium = serializers.CharField()
    large = serializers.CharField()

    @staticmethod
    def create(request, account: Account):
        """Get the URLs of alternative image sizes for the account."""
        return dict(
            [
                (size, request.build_absolute_uri(getattr(account.image, size)),)
                for size in ("small", "medium", "large")
            ]
        )
