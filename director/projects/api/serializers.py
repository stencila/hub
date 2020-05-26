from rest_framework import serializers
from rest_framework.fields import JSONField
from rest_polymorphic.serializers import PolymorphicSerializer


from accounts.models import Account
from assets.thema import themes
from lib.resource_allowance import QuotaName, resource_limit_met
from projects.project_models import Project, ProjectEvent, Snapshot
from projects.source_models import (
    Source,
    ElifeSource,
    GithubSource,
    GoogleDocsSource,
    GoogleDriveSource,
    PlosSource,
    UrlSource,
)


class ProjectAccountField(serializers.PrimaryKeyRelatedField):
    """
    Field for a project's account field.

    Limits the set of valid accounts for a project to those that
    the request user has modify or administer permissions.
    """

    def get_queryset(self):
        request = self.context.get("request", None)
        if request is None:
            return Account.objects.none()
        return Account.objects.filter(
            user_roles__user=request.user,
            user_roles__role__permissions__type__in=("modify", "administer"),
        ).distinct()


class ProjectSerializer(serializers.ModelSerializer):
    """Base serializer for projects."""

    account = ProjectAccountField(
        help_text="The account that the project is linked to."
    )

    public = serializers.BooleanField(
        default=False, help_text="Whether or not the project is publically visible."
    )

    theme = serializers.ChoiceField(
        choices=[(theme, theme.title()) for theme in themes],
        allow_blank=True,
        help_text="The default theme for the project.",
    )

    class Meta:
        model = Project
        fields = ["id", "account", "name", "description", "public", "theme"]

    def validate(self, data):
        """
        Validate the project fields.

        Checks that the account has sufficient quotas to
        create the project. This function is written to be able to used
        when either creating (self.instance is None) or updating
        (self.instance is not None) a project.
        """
        account = data.get("account")
        if account is None:
            account = self.instance.account
        assert account is not None

        public = data.get("public")
        if public is None:
            public = self.instance.public
        assert public is not None

        if resource_limit_met(account, QuotaName.MAX_PROJECTS):
            raise serializers.ValidationError(
                "The maximum number of projects for the account has been reached. "
                "Please upgrade the account subscription, or use a different account."
            )

        if not public and resource_limit_met(account, QuotaName.MAX_PRIVATE_PROJECTS):
            raise serializers.ValidationError(
                dict(
                    public="The maximum number of private projects for the account has been reached. "
                    "Please upgrade the account subscription, use a different account, or make the project public."
                )
            )

        return data


class ProjectCreateSerializer(ProjectSerializer):
    """
    Serializer used for creating a project.

    Set's the request user as the project creator.
    """

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Project
        fields = ProjectSerializer.Meta.fields + ["creator"]


class ProjectDestroySerializer(serializers.Serializer):
    """
    Serializer used when destroying a project.

    Requires the `name` of the project as confirmation that the user
    really wants to destroy it.
    """

    name = serializers.CharField(
        help_text="Confirm by providing the name of the project to be destroyed."
    )


class ProjectEventSerializer(serializers.ModelSerializer):
    log = JSONField()

    class Meta:
        model = ProjectEvent
        fields = [
            "id",
            "started",
            "finished",
            "message",
            "success",
            "project",
            "event_type",
            "log",
        ]


class SourceSerializer(serializers.ModelSerializer):
    """
    Base serializer for source instances.

    Project is read only to prevent a change to another
    project for which the user does not have permissions.
    """

    class Meta:
        model = Source
        exclude = ["polymorphic_ctype"]
        read_only_fields = ["creator", "created", "updated", "project"]


class ElifeSourceSerializer(SourceSerializer):
    class Meta:
        model = ElifeSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class GithubSourceSerializer(SourceSerializer):
    class Meta:
        model = GithubSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class GoogleDocsSourceSerializer(SourceSerializer):
    class Meta:
        model = GoogleDocsSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class GoogleDriveSourceSerializer(SourceSerializer):
    class Meta:
        model = GoogleDriveSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class PlosSourceSerializer(SourceSerializer):
    class Meta:
        model = PlosSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class UrlSourceSerializer(SourceSerializer):
    class Meta:
        model = UrlSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class SourcePolymorphicSerializer(PolymorphicSerializer):
    """Serializer which dispatches to the appropriate serializer depending upon source type."""

    resource_type_field_name = "type"

    model_serializer_mapping = {
        Source: SourceSerializer,
        ElifeSource: ElifeSourceSerializer,
        GithubSource: GithubSourceSerializer,
        GoogleDocsSource: GoogleDocsSourceSerializer,
        GoogleDriveSource: GoogleDriveSourceSerializer,
        PlosSource: PlosSourceSerializer,
        UrlSource: UrlSourceSerializer,
    }


class SnapshotSerializer(serializers.ModelSerializer):
    """The response data when creating or retreiving a snapshot."""

    # Use `number` instead of `version_number` in public API
    # for brevity, remove potential for casing inconsistencies,
    # and potentially to reduce confusion. e.g
    # "Is this the version of the snapshot?"
    number = serializers.IntegerField(source="version_number")

    class Meta:
        model = Snapshot
        fields = ["project", "number", "tag", "creator", "created", "completed"]
