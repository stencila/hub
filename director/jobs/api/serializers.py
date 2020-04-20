from rest_framework import serializers

from jobs.models import Job


class JobListSerializer(serializers.ModelSerializer):
    """
    A job serializer for the `list` view.

    This serializer includes all model fields with
    some made read only (i.e. can not be set in `create` or `update` views).
    """

    began = serializers.DateTimeField(read_only=True)
    ended = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    result = serializers.JSONField(read_only=True)
    error = serializers.CharField(read_only=True)
    log = serializers.JSONField(read_only=True)
    queue = serializers.CharField(read_only=True)
    worker = serializers.CharField(read_only=True)
    retries = serializers.IntegerField(read_only=True)
    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Job
        fields = "__all__"


class JobDetailSerializer(JobListSerializer):
    """
    A job serializer for detail views e.g. `create`, `retrieve`.

    Adds the `position` of the job in the queue.
    This involves another database query for each job
    so is probably best to avoid for lists.
    """

    position = serializers.IntegerField(read_only=True)
