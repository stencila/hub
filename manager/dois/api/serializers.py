from rest_framework import exceptions, serializers

from dois.models import Doi


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

    def validate_node(self, node):
        """
        Validate that the node is a supported type for DOIs.
        """
        valid_node_types = ("Article", "Review")
        if "type" not in node.json or node.json["type"] not in valid_node_types:
            raise exceptions.ValidationError(
                f"Node type must be one of {', '.join(valid_node_types)}"
            )
        return node

    def create(self, validated_data):
        """
        Create a DOI and dispatch a job to register it.
        """
        doi = super().create(validated_data)
        job = doi.register(self.context["request"].user)
        job.dispatch()
        return doi
