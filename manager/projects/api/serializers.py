import re

from django.db.models import Q
from rest_framework import exceptions, serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from accounts.api.serializers import AccountListSerializer
from accounts.models import Account, AccountQuotas, AccountTeam
from accounts.paths import AccountPaths
from manager.api.helpers import get_object_from_ident
from manager.api.validators import FromContextDefault
from manager.helpers import unique_slugify
from manager.themes import Themes
from projects.models.projects import Project, ProjectAgent, ProjectRole
from projects.models.snapshots import Snapshot
from projects.models.sources import (
    ElifeSource,
    GithubSource,
    GoogleDocsSource,
    GoogleDriveSource,
    PlosSource,
    Source,
    UploadSource,
    UrlSource,
)
from users.models import User


class ProjectAgentSerializer(serializers.ModelSerializer):
    """
    A serializer for project agents.

    Translates the `user` and `team` fields into
    `type` and `agent` (an id).
    """

    type = serializers.SerializerMethodField()

    agent = serializers.SerializerMethodField()

    class Meta:
        model = ProjectAgent
        fields = ["id", "project", "type", "agent", "role"]

    def get_type(self, instance):  # noqa: D102
        if instance.user:
            return "user"
        if instance.team:
            return "team"

    def get_agent(self, instance):  # noqa: D102
        if instance.user:
            return instance.user.id
        if instance.team:
            return instance.team.id


class ProjectAgentCreateSerializer(ProjectAgentSerializer):
    """
    A serializer for adding project agents.

    Includes an hidden field for the `project` and restricts
    the choices for `role`.
    """

    project = serializers.HiddenField(
        default=FromContextDefault(
            lambda context: get_object_from_ident(
                Project, context["view"].kwargs["project"]
            )
        )
    )

    type = serializers.ChoiceField(choices=["user", "team"], write_only=True)

    agent = serializers.IntegerField(write_only=True)

    role = serializers.ChoiceField(
        choices=[
            ProjectRole.AUTHOR.name,
            ProjectRole.MANAGER.name,
            ProjectRole.OWNER.name,
        ]
    )

    def validate(self, data):
        """
        Validate the data.

        - valid user or team id
        - no existing role for the agent
        """
        if data["type"] == "user":
            if User.objects.filter(id=data["agent"]).count() == 0:
                raise exceptions.ValidationError(
                    {"agent": "User with id {0} does not exist.".format(data["agent"])}
                )
        elif data["type"] == "team":
            if AccountTeam.objects.filter(id=data["agent"]).count() == 0:
                raise exceptions.ValidationError(
                    {"agent": "Team with id {0} does not exist.".format(data["agent"])}
                )

        if (
            ProjectAgent.objects.filter(
                Q(user_id=data["agent"]) | Q(team_id=data["agent"]),
                project=data["project"],
            ).count()
            > 0
        ):
            raise exceptions.ValidationError({"agent": "Already has a project role."})

        return data

    def create(self, validated_data):
        """Create the project agent."""
        return ProjectAgent.objects.create(
            project=validated_data["project"],
            user_id=validated_data["agent"]
            if validated_data["type"] == "user"
            else None,
            team_id=validated_data["agent"]
            if validated_data["type"] == "team"
            else None,
            role=validated_data["role"],
        )


class ProjectAgentUpdateSerializer(serializers.ModelSerializer):
    """
    A serializer for updating project agents.

    Only allows changing the `role` field (do not
    want to allow changing to a different project for example).
    """

    class Meta:
        model = ProjectAgent
        fields = "__all__"
        read_only_fields = ["id", "project", "user", "team"]


class ProjectAccountField(serializers.PrimaryKeyRelatedField):
    """
    Field for a project account.

    Sets the default to the name in the query.

    Limits the set of valid accounts for a project to those that
    the user is a member of.
    """

    def get_queryset(self):  # noqa: D102
        request = self.context.get("request", None)
        if request is None:
            return Account.objects.none()

        queryset = Account.objects.filter(users__user=request.user)

        account = request.GET.get("account")
        if account:
            queryset = queryset.filter(name=account)

        return queryset


class ProjectSerializer(serializers.ModelSerializer):
    """Base serializer for projects."""

    account = ProjectAccountField(help_text="The account that the project is owned by.")

    public = serializers.BooleanField(
        default=True, help_text="Should the project be publicly visible?"
    )

    name = serializers.CharField(help_text=Project._meta.get_field("name").help_text)

    theme = serializers.ChoiceField(
        choices=Themes.as_choices(),
        allow_blank=True,
        required=False,
        help_text="The default theme for the project.",
    )

    class Meta:
        model = Project
        fields = ["id", "account", "name", "title", "description", "public", "theme"]

    def validate(self, data):
        """
        Validate the project fields.

        TODO: Check that the user is a member of the account

        Also checks that the account has sufficient quotas to
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

        request = self.context.get("request")
        assert request is not None

        # If creating, then check that user is an account
        # member and check the quota for the total
        # number of projects
        if not self.instance:
            if (
                Account.objects.filter(name=account, users__user=request.user).count()
                == 0
            ):
                raise exceptions.PermissionDenied

            AccountQuotas.PROJECTS_TOTAL.check(account)

        # If creating or changing `public` then check quota for
        # the number of private projects.
        if data.get("public") and public is False:
            AccountQuotas.PROJECTS_PRIVATE.check(account)

        # Check the name is valid for this account
        name = data.get("name")
        if name:
            if AccountPaths.has(name):
                raise exceptions.ValidationError(
                    dict(name="Project name '{0}' is unavailable.".format(name))
                )

            if (
                Project.objects.filter(account=account, name=name)
                .exclude(id=self.instance.id if self.instance else None)
                .count()
            ):
                raise exceptions.ValidationError(
                    dict(
                        name="Project name '{0}' is already in use for this account.".format(
                            name
                        )
                    )
                )

            data["name"] = name = unique_slugify(
                name,
                instance=self.instance,
                queryset=Project.objects.filter(account=account),
            )

            MIN_LENGTH = 3
            if len(name) < MIN_LENGTH:
                raise exceptions.ValidationError(
                    dict(
                        name="Project name must have at least {0} valid characters.".format(
                            MIN_LENGTH
                        )
                    )
                )

            MAX_LENGTH = 64
            if len(name) > MAX_LENGTH:
                raise exceptions.ValidationError(
                    dict(
                        name="Project name must be less than {0} characters long.".format(
                            MAX_LENGTH
                        )
                    )
                )

        return data


class ProjectListSerializer(ProjectSerializer):
    """
    Serializer for listing projects.

    Includes the role of the user making the request.
    """

    role = serializers.CharField(
        read_only=True, help_text="Role of the current user on the project (if any)."
    )

    account = AccountListSerializer()

    class Meta:
        model = Project
        fields = ProjectSerializer.Meta.fields + ["role"]


class ProjectCreateSerializer(ProjectSerializer):
    """
    Serializer for creating a project.

    Set's the request user as the project creator.
    """

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Project
        fields = ProjectSerializer.Meta.fields + ["creator"]


ProjectRetrieveSerializer = ProjectSerializer

ProjectUpdateSerializer = ProjectSerializer


class ProjectDestroySerializer(serializers.Serializer):
    """
    Serializer for destroying a project.

    Requires the `name` of the project as confirmation that the user
    really wants to destroy it.
    """

    name = serializers.CharField(
        help_text="Confirm by providing the name of the project to be destroyed."
    )

    def validate_name(self, value):
        """Validate that the provided name matches."""
        if value != self.instance.name:
            raise exceptions.ValidationError(
                "Provided name does not match the project name."
            )


class SnapshotSerializer(serializers.ModelSerializer):
    """
    A serializer for snapshots.
    """

    project = serializers.HiddenField(
        default=FromContextDefault(
            lambda context: get_object_from_ident(
                Project, context["view"].kwargs["project"]
            )
        )
    )

    class Meta:
        model = Snapshot
        fields = "__all__"
        read_only_fields = ["id", "project", "creator", "created", "job"]

    def create(self, validated_data):
        project = validated_data.get("project")
        assert project is not None

        request = self.context.get("request")
        assert request is not None

        return Snapshot.create(project, request.user)


class SourceSerializer(serializers.ModelSerializer):
    """
    Base serializer for source instances.

    Project is read only to prevent a change to another
    project for which the user does not have permissions.
    """

    project = serializers.HiddenField(
        default=FromContextDefault(
            lambda context: get_object_from_ident(
                Project, context["view"].kwargs["project"]
            )
        )
    )

    class Meta:
        model = Source
        exclude = ["polymorphic_ctype"]
        read_only_fields = ["creator", "created", "updated", "project"]

    def validate_path(self, value):
        """
        Validate the path field.

        Splits into parts and checks that it each part only contains valid
        characters.
        """
        for part in value.split("/"):
            match = re.search(r"^[A-Za-z][A-Za-z0-9\.\-_ ]*$", part, re.I)
            if not match:
                raise exceptions.ValidationError(
                    'Path contains an invalid part: "{0}"'.format(part)
                )
        return value

    def validate(self, data):
        """
        Validate that the path does not yet exist for the project.
        """
        project = data.get("project", self.instance.project if self.instance else None)
        path = data.get("path", self.instance.path if self.instance else None)
        id = self.instance.id if self.instance else None

        if Source.objects.filter(project=project, path=path).exclude(id=id).count():
            raise exceptions.ValidationError(
                dict(path="A source with this path already exists in the project.")
            )
        return data


class ElifeSourceSerializer(SourceSerializer):
    """
    Serializer for eLife sources.
    """

    class Meta:
        model = ElifeSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class GithubSourceSerializer(SourceSerializer):
    """
    Serializer for GitHub sources.
    """

    url = serializers.CharField(
        required=False, allow_blank=True, help_text="The URL of the repository."
    )

    repo = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="A GitHub repository name (e.g. org/name).",
    )

    class Meta:
        model = GithubSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields

    def validate(self, data):
        """
        Validate the url field.
        """
        url = data.get("url")
        repo = data.get("repo")
        if url:
            address = GithubSource.parse_address(url, strict=True)
            del data["url"]
            data["repo"] = address.repo
            data["subpath"] = address.subpath
            return data
        elif repo:
            if not re.match(r"^(?:[a-z0-9\-]+)/(?:[a-z0-9\-_]+)$"):
                raise exceptions.ValidationError(
                    dict(repo="Not a valid GitHub repository name.")
                )
            return data
        else:
            raise exceptions.ValidationError(
                dict(
                    url="Please provide either a GitHub URL or a GitHub repository name."
                )
            )

        return super.validate()


class GoogleDocsSourceSerializer(SourceSerializer):
    """
    Serializer for Google Docs sources.
    """

    doc_id = serializers.CharField(
        help_text="A Google Doc id e.g. 1iNeKTbnIcW_92Hmc8qxMkrW2jPrvwjHuANju2hkaYkA, or its "
        "URL e.g https://docs.google.com/document/d/1iNeKTbnIcW_92Hmc8qxMkrW2jPrvwjHuANju2hkaYkA/edit"
    )

    class Meta:
        model = GoogleDocsSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields

    def validate_doc_id(self, value):
        """
        Validate the document id.
        """
        return GoogleDocsSource.parse_address(value, naked=True, strict=True).doc_id


class GoogleDriveSourceSerializer(SourceSerializer):
    """
    Serializer for Google Drive sources.
    """

    class Meta:
        model = GoogleDriveSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class PlosSourceSerializer(SourceSerializer):
    """
    Serializer for PLOS sources.
    """

    class Meta:
        model = PlosSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class UploadSourceSerializer(SourceSerializer):
    """
    Serializer for uploaded sources.
    """

    class Meta:
        model = UploadSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class UrlSourceSerializer(SourceSerializer):
    """
    Serializer for URL sources.
    """

    class Meta:
        model = UrlSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class SourcePolymorphicSerializer(PolymorphicSerializer):
    """
    Serializer which dispatches to the appropriate serializer depending upon source type.
    """

    resource_type_field_name = "type"

    model_serializer_mapping = {
        Source: SourceSerializer,
        ElifeSource: ElifeSourceSerializer,
        GithubSource: GithubSourceSerializer,
        GoogleDocsSource: GoogleDocsSourceSerializer,
        GoogleDriveSource: GoogleDriveSourceSerializer,
        PlosSource: PlosSourceSerializer,
        UploadSource: UploadSourceSerializer,
        UrlSource: UrlSourceSerializer,
    }

    class_name_serializer_mapping = dict(
        [
            (model.__name__, serializer)
            for model, serializer in model_serializer_mapping.items()
        ]
    )
