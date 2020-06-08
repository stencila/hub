from rest_framework import exceptions, serializers

from accounts.models import Account, AccountRole, AccountUser, Team
from manager.api.helpers import get_object_from_ident
from manager.api.validators import FromContextDefault
from users.api.serializers import UserIdentifierSerializer, UserSerializer
from users.models import User


class AccountUserSerializer(serializers.ModelSerializer):
    """
    A serializer for account users.

    Includes a nested serializer for the user
    """

    user = UserSerializer()

    class Meta:
        model = AccountUser
        fields = "__all__"


class AccountUserCreateSerializer(UserIdentifierSerializer):
    """
    A serializer for adding account users.

    Includes a nested serializer for the user
    """

    account = serializers.HiddenField(
        default=FromContextDefault(
            lambda context: get_object_from_ident(
                Account, context["view"].kwargs["account"]
            )
        )
    )

    role = serializers.ChoiceField(
        choices=[
            AccountRole.MEMBER.name,
            AccountRole.MANAGER.name,
            AccountRole.ADMIN.name,
        ]
    )

    def create(self, validated_data):
        return AccountUser.objects.create(
            account=validated_data["account"],
            user=validated_data["user"],
            role=validated_data["role"],
        )


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


class TeamDestroySerializer(serializers.Serializer):
    """
    A serializer for destroying a team.

    Requires the `name` of the team as confirmation that the user
    really wants to destroy it.
    """

    name = serializers.CharField(
        required=True,
        help_text="Confirm by providing the name of the team to be destroyed.",
    )

    def validate_name(self, value):
        """Validate that the provided name matches."""
        if value != self.instance.name:
            raise exceptions.ValidationError(
                dict(name="Provided name does not match the team name.")
            )


class AccountSerializer(serializers.ModelSerializer):
    """
    A serializer for accounts.

    Includes only basic model fields.
    """

    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "user",
            "creator",
            "created",
            "display_name",
            "location",
            "image",
            "website",
            "email",
            "theme",
            "hosts",
        ]


class AccountCreateSerializer(AccountSerializer):
    """
    A serializer for creating accounts.

    Gets `creator` from the request user.
    """

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

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
