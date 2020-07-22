from rest_framework import exceptions, serializers

from accounts.models import Account, AccountRole, AccountTeam, AccountUser
from accounts.quotas import AccountQuotas
from manager.api.helpers import get_object_from_ident
from manager.api.validators import FromContextDefault
from manager.helpers import unique_slugify
from manager.paths import RootPaths
from manager.themes import Themes
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
            AccountRole.OWNER.name,
        ]
    )

    def create(self, validated_data):  # noqa: D102
        return AccountUser.objects.create(
            account=validated_data["account"],
            user=validated_data["user"],
            role=validated_data["role"],
        )


class AccountTeamSerializer(serializers.ModelSerializer):
    """
    A serializer for teams.

    Includes only basic model fields.
    """

    name = serializers.CharField(help_text=Account._meta.get_field("name").help_text)

    members = UserSerializer(read_only=True, many=True)

    class Meta:
        model = AccountTeam
        fields = [
            "id",
            "account",
            "name",
            "description",
            "members",
        ]

    def validate(self, data):
        """
        Slugify and validate the name field.

        Needs to be done in `validate` (not `validate_name`) so that the
        account is also available.
        """
        account = self.instance.account if self.instance else data.get("account")
        assert account is not None

        name = unique_slugify(
            data["name"],
            instance=self.instance,
            queryset=AccountTeam.objects.filter(account=account),
        )

        MIN_LENGTH = 3
        if len(name) < MIN_LENGTH:
            raise exceptions.ValidationError(
                dict(
                    name="Team name must have at least {0} valid characters.".format(
                        MIN_LENGTH
                    )
                )
            )

        MAX_LENGTH = 64
        if len(name) > MAX_LENGTH:
            raise exceptions.ValidationError(
                dict(
                    name="Team name must be less than {0} characters long.".format(
                        MAX_LENGTH
                    )
                )
            )

        data["name"] = name
        return data


class AccountTeamCreateSerializer(AccountTeamSerializer):
    """
    A serializer for creating teams.

    - Based on the default team serializer
    - Makes the `account` field readonly, and based on the `account`
      URL parameter, so that it is not possible to create a team
      for a different account.
    - Makes `members` optional.
    """

    class Meta:
        model = AccountTeam
        fields = AccountTeamSerializer.Meta.fields
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


class AccountTeamUpdateSerializer(AccountTeamCreateSerializer):
    """
    A serializer for updating teams.

    - Based on the `create` serializer.
    - Does not allow the `account` to be changed.
    """

    class Meta:
        model = AccountTeam
        fields = AccountTeamCreateSerializer.Meta.fields
        read_only_fields = ["account"]
        ref_name = None


class AccountTeamDestroySerializer(serializers.Serializer):
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
    Checks that the account `name` is not a reserved path
    and not already in use.
    """

    name = serializers.CharField(help_text=Account._meta.get_field("name").help_text)

    theme = serializers.ChoiceField(
        choices=Themes.as_choices(),
        allow_blank=True,
        required=False,
        help_text="The default theme for the account.",
    )

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

    def validate_name(self, name):
        """
        Slugify and validate the name field.

        The `unique_slugify` function will automatically avoid
        duplication (by appending digits). To let the user know
        of similar account names, we manually check for duplicates
        before that is called.
        """
        if RootPaths.has(name):
            raise exceptions.ValidationError(
                "Account name '{0}' is unavailable.".format(name)
            )

        if (
            Account.objects.filter(name=name)
            .exclude(id=self.instance.id if self.instance else None)
            .count()
        ):
            raise exceptions.ValidationError(
                "Account name '{0}' is already in use.".format(name)
            )

        name = unique_slugify(
            name, instance=self.instance, queryset=Account.objects.all()
        )

        MIN_LENGTH = 3
        if len(name) < MIN_LENGTH:
            raise exceptions.ValidationError(
                "Account name must have at least {0} valid characters.".format(
                    MIN_LENGTH
                )
            )

        MAX_LENGTH = 64
        if len(name) > MAX_LENGTH:
            raise exceptions.ValidationError(
                "Account name must be less than {0} characters long.".format(MAX_LENGTH)
            )

        return name


class AccountCreateSerializer(AccountSerializer):
    """
    A serializer for creating accounts.

    Gets `creator` from the request user.
    """

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Account
        fields = AccountSerializer.Meta.fields

    def validate(self, data):
        """
        Validate the data.

        Checks that the user has not exceeded the number
        of accounts that they can create. This is primarily an anti-spamming
        check.
        """
        AccountQuotas.ORGS_CREATED.check(data["creator"].personal_account)
        return data


class AccountListSerializer(AccountSerializer):
    """
    A serializer for listing accounts.

    Includes the role of the user making the request.
    """

    role = serializers.CharField(
        read_only=True, help_text="Role of the current user on the account (if any)."
    )

    class Meta:
        model = Account
        fields = AccountSerializer.Meta.fields + ["role"]


class AccountRetrieveSerializer(AccountListSerializer):
    """
    A serializer for retrieving accounts.

    Includes more details on the account:

    - the account users
    - the account teams
    """

    users = AccountUserSerializer(read_only=True, many=True)

    teams = AccountTeamSerializer(read_only=True, many=True)

    class Meta:
        model = Account
        fields = AccountListSerializer.Meta.fields + ["users", "teams"]


def get_user_field(field_name: str):
    """Get a field from the user (if any) of the account."""

    def getter(context):
        account = context["view"].get_object()
        if account and account.user:
            return getattr(account.user, field_name) or ""
        return ""

    return getter


class AccountUpdateSerializer(AccountSerializer):
    """
    A serializer for updating accounts.

    Makes some fields read only. For personal accounts, allows the user's
    first and last names (which are stored on the `User` model) to be
    updated via this serializer.
    """

    first_name = serializers.CharField(
        default=FromContextDefault(get_user_field("first_name")),
        help_text="Your first names (given names).",
    )

    last_name = serializers.CharField(
        default=FromContextDefault(get_user_field("last_name")),
        help_text="Your last names (family names, surnames).",
    )

    class Meta:
        model = Account
        fields = AccountSerializer.Meta.fields + ["first_name", "last_name"]
        read_only_fields = ["creator", "created"]

    def save(self):
        """
        If this is a personal account, then set user first and last names.

        Update the account's display name to be a concatenation of the first and last names.
        """
        user = self.instance.user
        if user:
            if "first_name" in self.validated_data:
                user.first_name = self.validated_data["first_name"]
            if "last_name" in self.validated_data:
                user.last_name = self.validated_data["last_name"]
            user.save()
            self.validated_data["display_name"] = (
                (user.first_name or "") + " " + (user.last_name or "")
            ).strip()
        return super().save()
