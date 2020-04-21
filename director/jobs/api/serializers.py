from django.shortcuts import reverse
from rest_framework import serializers

from jobs.models import Job, JobMethod


class JobListSerializer(serializers.ModelSerializer):
    """
    A job serializer for the `list` action.

    This serializer includes all model fields.
    Some are made read only in derived serializers
    (e.g. can not be set in `create` or `update` views).
    """

    class Meta:
        model = Job
        fields = "__all__"

    url_global = serializers.SerializerMethodField()

    def get_url_global(self, job: Job):
        """
        Get the URL that a user can connect to the job
        from outside the local network.

        Will be `None` if the job does not have an
        internal URL or has ended.
        """
        if job.url and not job.ended:
            request = self.context.get("request")
            return request.build_absolute_uri(
                reverse("api-jobs-connect", kwargs={"pk": job.id})
            )


class JobRetrieveSerializer(JobListSerializer):
    """
    A job serializer for the `retrieve` action.

    Adds the `position` of the job in the queue.
    This involves another database query for each job
    so is probably best to avoid for lists.
    """

    position = serializers.IntegerField(read_only=True)


class JobCreateSerializer(JobRetrieveSerializer):
    """
    A job serializer for the `create` action.

    Makes most fields readonly (ie. can not be set),
    makes some fields required.
    """

    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    method = serializers.ChoiceField(choices=JobMethod.as_choices(), required=True)
    params = serializers.JSONField(required=False)

    status = serializers.CharField(read_only=True)
    began = serializers.DateTimeField(read_only=True)
    ended = serializers.DateTimeField(read_only=True)
    result = serializers.JSONField(read_only=True)
    url = serializers.CharField(read_only=True)
    log = serializers.JSONField(read_only=True)
    queue = serializers.CharField(read_only=True)
    worker = serializers.CharField(read_only=True)
    retries = serializers.IntegerField(read_only=True)


class JobUpdateSerializer(JobRetrieveSerializer):
    """
    A job serializer for the `update` and `partial_update` actions.

    Intended for `worker``. Makes some fields read only (should not be
    changed after creation) but allows workers to update
    values of rest.
    """

    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    method = serializers.CharField(read_only=True)
    params = serializers.DateTimeField(read_only=True)
