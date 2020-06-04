from rest_framework import serializers

from accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):
    """
    A serializer for accounts.

    Includes only basic model fields.
    Derived serializers add other derived fields (which may
    require extra queries) and make some read only.
    """

    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "user",
            "creator",
            "created",
            "image",
            "theme",
            "hosts",
        ]


class AccountCreateUpdateSerializer(AccountSerializer):
    """
    A serializer for creating and updating accounts.

    Makes certain fields read only.
    """

    class Meta:
        model = Account
        fields = AccountSerializer.Meta.fields
        read_only_fields = ["id", "creator", "created"]
