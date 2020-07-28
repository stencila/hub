from django.shortcuts import reverse
from rest_framework import serializers

from accounts.models import Account
from jobs.models import Job, JobMethod, Queue, Worker, WorkerHeartbeat, Zone
from manager.api.helpers import get_object_from_ident
from manager.api.validators import FromContextDefault
from projects.models.projects import Project


class JobListSerializer(serializers.ModelSerializer):
    """
    A job serializer for the `list` action.

    This serializer includes all model fields.
    Some are made read only in derived serializers
    (e.g. can not be set in `create` or `update` views).

    Also adds "cheap to calculate" properties derived from other
    fields. e.g. `summary_string`
    """

    summary_string = serializers.CharField(read_only=True)

    runtime_formatted = serializers.CharField(read_only=True)

    url = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = "__all__"
        ref_name = None

    def get_url(self, job: Job):
        """
        Get the URL to connect to the job from outside the local network.

        Will be `None` if the job does not have an
        internal URL or has ended.
        """
        if job.url and job.is_active:
            request = self.context.get("request")
            return request.build_absolute_uri(
                reverse(
                    "api-projects-jobs-connect",
                    kwargs=dict(project=job.project.id, job=job.id),
                )
            )


class JobRetrieveSerializer(JobListSerializer):
    """
    A job serializer for the `retrieve` action.

    Adds the `position` of the job in the queue.
    This involves another database query for each job
    so is probably best to avoid for lists.
    """

    position = serializers.IntegerField(read_only=True)
    children = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Job
        fields = "__all__"
        ref_name = "Job"


class JobCreateSerializer(JobRetrieveSerializer):
    """
    A job serializer for the `create` action.

    Makes most fields readonly (ie. can not be set),
    makes some fields required.
    """

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = [
            "creator",
            "created",
            "project",
            "zone",
            "queue",
            "status",
            "began",
            "ended",
            "result",
            "url",
            "log",
            "runtime",
            "users",
            "retries",
            "worker",
        ]
        ref_name = None

    project = serializers.HiddenField(
        default=FromContextDefault(
            lambda context: get_object_from_ident(
                Project, context["view"].kwargs["project"]
            )
        )
    )
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    method = serializers.ChoiceField(choices=JobMethod.as_choices(), required=True)
    params = serializers.JSONField(required=False)

    # TODO: allow for project and zone to be specified; validate each against user / account

    def create(self, validated_data):
        """
        Create and dispatch a job.
        """
        job = super().create(validated_data)
        job.dispatch()
        return job


class JobUpdateSerializer(JobRetrieveSerializer):
    """
    A job serializer for the `update` and `partial_update` actions.

    Intended for internal services to update job status.
    Makes some fields read only (should not be
    changed after creation) but allows updating of the rest.
    """

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = ["creator", "created", "method", "params", "zone", "queue"]
        ref_name = None


class ZoneSerializer(serializers.ModelSerializer):
    """
    A zone serializer.

    Includes all model fields.
    """

    class Meta:
        model = Zone
        fields = "__all__"


class ZoneCreateSerializer(ZoneSerializer):
    """
    A zone serializer for the `create` action.

    Makes `account` readonly, and based on the URL parameter
    so that it is not possible to create a zone for a different account.
    Also validates `name` is unique within an account.
    """

    class Meta:
        model = Zone
        fields = "__all__"
        ref_name = None

    account = serializers.HiddenField(
        default=FromContextDefault(
            lambda context: get_object_from_ident(
                Account, context["view"].kwargs["account"]
            )
        )
    )

    def validate(self, data):
        """Validate that the zone name is unique for the account."""
        if Zone.objects.filter(account=data["account"], name=data["name"]).count() != 0:
            raise serializers.ValidationError(
                dict(name="Zone name must be unique for account.")
            )
        return data


class QueueSerializer(serializers.ModelSerializer):
    """
    A queue serializer.

    Given this is only ever used read-only, it includes all model fields.
    """

    class Meta:
        model = Queue
        fields = "__all__"


class WorkerSerializer(serializers.ModelSerializer):
    """
    A worker serializer.

    Given this is only ever used read-only, it includes all model fields.
    """

    active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Worker
        fields = "__all__"


class WorkerHeartbeatSerializer(serializers.ModelSerializer):
    """
    A worker heartbeat serializer.

    Given this is only used for a particular worker, it excludes the
    both the heartbeat's and the worker's id fields.
    """

    class Meta:
        model = WorkerHeartbeat
        exclude = ["id", "worker"]
