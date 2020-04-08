from rest_framework import serializers
from rest_framework.fields import JSONField

from projects.project_models import Project, ProjectEvent, Snapshot


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "account", "name", "description", "public"]


class ProjectEventSerializer(serializers.ModelSerializer):
    log = JSONField()
    project = ProjectSerializer()

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


class SnapshotCreateRequestSerializer(serializers.ModelSerializer):
    """The request data when creating a snapshot."""

    class Meta:
        model = Snapshot
        fields = ["tag"]
        ref_name = None
