from typing import Optional

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.db.models import Q
from django.urls import reverse
from drf_yasg.utils import swagger_serializer_method
from knox.models import AuthToken
from rest_framework import serializers

from accounts.api.serializers_account_image import AccountImageSerializer
from accounts.models import Account
from users.models import (
    Invite,
    User,
    get_feature_flags,
    get_orgs_summary,
    get_projects_summary,
)


class UserSerializer(serializers.ModelSerializer):
    """
    A serializer for public user details.

    Only fields considered public should be available here.
    Includes fields from the user's personal `Account`.
    """

    display_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()
    public_email = serializers.SerializerMethodField()

    def get_personal_account_attr(self, user: User, attr: str) -> Optional[str]:
        """Get an attribute of a user's personal account."""
        try:
            return getattr(user.personal_account, attr, None)
        except User.personal_account.RelatedObjectDoesNotExist:
            return None

    def get_display_name(self, user) -> Optional[str]:
        """Get the display name of the user's personal account."""
        return self.get_personal_account_attr(user, "display_name")

    def get_location(self, user) -> Optional[str]:
        """Get the location for the user's personal account."""
        return self.get_personal_account_attr(user, "location")

    @swagger_serializer_method(serializer_or_field=AccountImageSerializer)
    def get_image(self, user) -> Optional[dict]:
        """Get the URLs of alternative image sizes for the account."""
        request = self.context.get("request")
        try:
            account = user.personal_account
        except User.personal_account.RelatedObjectDoesNotExist:
            return None
        return AccountImageSerializer.create(request, account) if request else None

    def get_website(self, user) -> Optional[str]:
        """Get the website of the user's personal account."""
        return self.get_personal_account_attr(user, "website")

    def get_public_email(self, user) -> Optional[str]:
        """Get the email address of the user's personal account."""
        return self.get_personal_account_attr(user, "email")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "display_name",
            "location",
            "image",
            "website",
            "public_email",
        ]


class MeEmailAddressSerializer(serializers.ModelSerializer):
    """
    An email address linked to a user.
    """

    class Meta:
        model = EmailAddress
        fields = ["email", "primary", "verified"]


class MeLinkedAccountSerializer(serializers.ModelSerializer):
    """
    An external, third party account linked to a user.
    """

    class Meta:
        model = SocialAccount
        fields = ["provider", "uid", "date_joined", "last_login"]


class PersonalAccountSerializer(serializers.ModelSerializer):
    """
    The user's own personal account.
    """

    class Meta:
        model = Account
        fields = ["id", "tier"]


class MeFeatureFlagsSerializer(serializers.Serializer):
    """
    Serializer for a user's feature flag settings.

    This is here simply for documentation purposes (`drf-yasg`
    requires a `serializer_class` on views). The actual properties
    are dynamic, based on database rows.
    """

    feature_flag = serializers.ChoiceField(["on", "off"])


class MeSerializer(UserSerializer):
    """
    A serializer for a user's own details.

    Adds fields that are private to the user.
    """

    email_addresses = MeEmailAddressSerializer(
        source="emailaddress_set", many=True, read_only=True
    )

    linked_accounts = MeLinkedAccountSerializer(
        source="socialaccount_set", many=True, read_only=True
    )

    personal_account = PersonalAccountSerializer()

    orgs_summary = serializers.SerializerMethodField()

    projects_summary = serializers.SerializerMethodField()

    feature_flags = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + [
            "date_joined",
            "last_login",
            "email_addresses",
            "linked_accounts",
            "personal_account",
            "orgs_summary",
            "projects_summary",
            "feature_flags",
        ]

    def get_orgs_summary(self, user):
        """Get a summary of organizations that the user is a member ofr."""
        return get_orgs_summary(user)

    def get_projects_summary(self, user):
        """Get a summary of projects for the user."""
        return get_projects_summary(user)

    def get_feature_flags(self, user):
        """Get a dictionary of feature flags for the user."""
        return get_feature_flags(user)


class UserIdentifierSerializer(serializers.Serializer):
    """
    A serializer for specifying a user.

    Allow client to specify the user using either their
    `id` or `username`. Used for POSTing users to lists
    e.g. team membership
    """

    id = serializers.IntegerField(required=False)

    username = serializers.CharField(required=False)

    def validate(self, data):
        """
        Validate the suppied data.

        Check that either is or username is provided
        and that the user exists.
        """
        if "id" not in data and "username" not in data:
            raise serializers.ValidationError("One of `id` or `username` is required")
        try:
            data["user"] = User.objects.get(
                Q(id=data.get("id")) | Q(username=data.get("username"))
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return data


class TokenSerializer(serializers.ModelSerializer):
    """
    A serializer for user tokens.

    Renames the `token_key` field to `id`.
    """

    id = serializers.CharField(
        source="token_key", help_text="First eight characters of the token."
    )

    class Meta:
        model = AuthToken
        fields = ["user", "id", "created", "expiry"]


class InviteSerializer(serializers.ModelSerializer):
    """
    A serializer for invites.
    """

    url = serializers.SerializerMethodField()

    class Meta:
        model = Invite
        fields = "__all__"
        read_only_fields = ["key"]

    def get_url(self, obj) -> str:
        """Get the absolute URL for the invite."""
        request = self.context["request"]
        return request.build_absolute_uri(
            reverse("ui-users-invites-accept", args=[obj.key])
        )

    def create(self, data):
        """Create and send the invite."""
        request = self.context["request"]
        invite = Invite.objects.create(**data, inviter=request.user)
        invite.send_invitation(request)
        return invite
