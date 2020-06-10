from rest_framework import serializers

from accounts.models import Account, AccountQuota
from projects.models import Project


class ProjectAccountField(serializers.PrimaryKeyRelatedField):
    """
    Field for a project account.

    Limits the set of valid accounts for a project to those that
    the user is a member of.
    """

    def get_queryset(self):
        request = self.context.get("request", None)
        if request is None:
            return Account.objects.none()
        return Account.objects.filter(users__user=request.user,).distinct()


class ProjectSerializer(serializers.ModelSerializer):
    """Base serializer for projects."""

    account = ProjectAccountField(help_text="The account that the project is owned by.")

    public = serializers.BooleanField(
        default=False, help_text="Should the project is publically visible?"
    )

    theme = serializers.ChoiceField(
        choices=[],  # TODO
        allow_blank=True,
        help_text="The default theme for the project.",
    )

    class Meta:
        model = Project
        fields = ["id", "account", "name", "title", "description", "public", "theme"]

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

        AccountQuota.PROJECTS_TOTAL.check(account)

        if not public:
            AccountQuota.PROJECTS_PRIVATE.check(account)

        return data


class ProjectCreateSerializer(ProjectSerializer):
    """
    Serializer used when creating a project.

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
