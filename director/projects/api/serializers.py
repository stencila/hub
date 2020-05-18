from rest_framework import serializers
from rest_framework.fields import JSONField
from rest_polymorphic.serializers import PolymorphicSerializer


from projects.project_models import Project, ProjectEvent, Snapshot
from projects.source_models import (
    Source,
    ElifeSource,
    PlosSource,
    UrlSource,
    GoogleDocsSource,
)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "account", "name", "description", "public", "theme"]


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


class GoogleDocsSourceSerializer(SourceSerializer):
    class Meta:
        model = GoogleDocsSource
        exclude = SourceSerializer.Meta.exclude
        read_only_fields = SourceSerializer.Meta.read_only_fields


class SourcePolymorphicSerializer(PolymorphicSerializer):
    """Serializer which dispatches to the appropriate serializer depending uponsource type."""

    resource_type_field_name = "type"

    model_serializer_mapping = {
        Source: SourceSerializer,
        ElifeSource: ElifeSourceSerializer,
        PlosSource: PlosSourceSerializer,
        UrlSource: UrlSourceSerializer,
        GoogleDocsSource: GoogleDocsSourceSerializer,
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
