from rest_framework import exceptions, serializers

from accounts.quotas import AccountQuotas
from dois.models import Doi
from users.models import get_projects


class DoiSerializer(serializers.ModelSerializer):
    """
    A serializer for DOIs.
    """

    doi = serializers.CharField(read_only=True)

    url = serializers.CharField(read_only=True)

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Doi
        exclude = [
            "job",
            "deposit_request",
            "deposit_response",
            "registration_response",
        ]

    def validate(self, data):
        """
        Validate data before creating a DOI.

        Validate that the node is a supported type and is linked to a project.
        Check that the creator has sufficient permissions and the project's account
        has sufficient quota.
        """
        node = data["node"]
        creator = data["creator"]

        valid_node_types = ("Article", "Review")
        if "type" not in node.json or node.json["type"] not in valid_node_types:
            raise exceptions.ValidationError(
                dict(node=f"Node type must be one of {', '.join(valid_node_types)}.")
            )

        project = node.project
        if not project:
            raise exceptions.ValidationError(
                dict(node="Node must be linked to a project.")
            )

        role = get_projects(creator).get(id=project.id).role
        if role not in ["MANAGER", "OWNER"]:
            raise exceptions.PermissionDenied(
                "You need to be the project manager or owner to create a DOI for it."
            )

        AccountQuotas.DOIS_CREATED_MONTH.check(project.account)

        return data

    def create(self, validated_data):
        """
        Create a DOI and dispatch a job to register it.
        """
        doi = super().create(validated_data)
        job = doi.register(self.context["request"].user)
        job.dispatch()
        return doi
