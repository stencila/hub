from rest_framework import serializers

from accounts.models import Account, AccountUser, Team
from manager.api.helpers import get_object_from_ident
from manager.api.validators import FromContextDefault
from users.api.serializers import UserSerializer
from users.models import User


class TeamSerializer(serializers.ModelSerializer):
    """
    A serializer for teams.

    Includes only basic model fields.
    """

    members = UserSerializer(read_only=True, many=True)

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

    - Based on the default team serializer
    - Makes the `account` field readonly, and based on the `account`
      URL parameter, so that it is not possible to create a team
      for a different account.
    - Makes `members` optional.
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


class AccountUserSerializer(serializers.ModelSerializer):
    """
    A serializer for account users.

    Includes a nested serializer for the user
    """

    user = UserSerializer()

    class Meta:
        model = AccountUser
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    """
    A serializer for accounts.

    Includes only basic model fields.
    """

    class Meta:
        model = Account
        fields = ["id", "name", "user", "creator", "created", "image", "theme", "hosts"]


class AccountCreateSerializer(AccountSerializer):
    """
    A serializer for creating accounts.

    Gets `creator` from the request user
    and makes `users` optional.
    """

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # TODO
    # users = serializers.PrimaryKeyRelatedField(
    #    required=False, queryset=User.objects.all(), many=True
    # )

    class Meta:
        model = Account
        fields = AccountSerializer.Meta.fields


class AccountRetrieveSerializer(AccountSerializer):
    """
    A serializer for retrieving accounts.

    Includes more details on the account:

    - the account users
    - the account teams
    """

    users = AccountUserSerializer(read_only=True, many=True)

    teams = TeamSerializer(read_only=True, many=True)

    class Meta:
        model = Account
        fields = AccountSerializer.Meta.fields + ["users", "teams"]


class AccountUpdateSerializer(AccountSerializer):
    """
    A serializer for updating accounts.

    Makes some fields read only.
    """

    class Meta:
        model = Account
        fields = AccountSerializer.Meta.fields
        read_only_fields = ["creator", "created"]
