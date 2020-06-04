from rest_framework import serializers

from accounts.models import Account, Team
from manager.api.helpers import get_filter_from_ident, get_object_from_ident
from manager.api.validators import FromContextDefault
from users.models import User


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


class TeamSerializer(serializers.ModelSerializer):
    """
    A serializer for teams.

    Includes only basic model fields.
    Derived serializers add other derived fields (which may
    require extra queries) and make some read only.
    """

    class Meta:
        model = Team
        fields = [
            "id",
            "account",
            "name",
            "description",
            "members",
        ]


class TeamCreateSerializer(TeamSerializer):
    """
    A serializer for creating teams.

    - Makes the `account` field readonly, and based on the `account` URL parameter
      so that it is not possible to create a team for a different account.
    - Makes `members` optional.
    - Validates `name` is unique within the account.
    """

    class Meta:
        model = Team
        fields = TeamSerializer.Meta.fields
        ref_name = None

    account = serializers.HiddenField(
        default=FromContextDefault(
            lambda context: get_object_from_ident(
                Account, context["view"].kwargs["account"]
            )
        )
    )

    members = serializers.PrimaryKeyRelatedField(
        required=False, queryset=User.objects.all(), many=True
    )

    def validate_name(self, name: str) -> str:
        """Check that the team name is unique for the account."""
        if (
            Team.objects.filter(
                **get_filter_from_ident(
                    self.context["view"].kwargs["account"], prefix="account"
                ),
                name=name
            ).count()
            != 0
        ):
            raise serializers.ValidationError("Team name must be unique for account.")
        return name


class TeamUpdateSerializer(TeamCreateSerializer):
    """
    A serializer for updating teams.

    - Based on the `create` serializer.
    - Does not allow the `account` to be changed.
    """

    class Meta:
        model = Team
        fields = TeamCreateSerializer.Meta.fields
        read_only_fields = ["account"]
        ref_name = None
