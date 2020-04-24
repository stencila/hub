from django.shortcuts import reverse
from rest_framework import serializers

from accounts.models import Account
from general.api.validators import FromContextDefault
from jobs.models import Job, JobMethod, JobStatus, Zone


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
        ref_name = None

    url_global = serializers.SerializerMethodField()

    def get_url_global(self, job: Job):
        """
        Get the URL to connect to the job from outside the local network.

        Will be `None` if the job does not have an
        internal URL or has ended.
        """
        if job.url and not job.ended and not JobStatus.has_ended(job.status):
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

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    method = serializers.ChoiceField(choices=JobMethod.as_choices(), required=True)
    params = serializers.JSONField(required=False)

    # TODO: allow for project and zone to be specified; validate each against user / account


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

    Makes `account` readonly, and based on the `pk` URL parameter
    so that it is not possible to create a zone for a different account.
    Also validates `name` is unique within an account.
    """

    class Meta:
        model = Zone
        fields = "__all__"

    account = serializers.HiddenField(
        default=FromContextDefault(
            lambda context: Account.objects.get(id=context["view"].kwargs["pk"])
        )
    )

    def validate_name(self, name: str) -> str:
        pk = self.context["view"].kwargs["pk"]
        if Zone.objects.filter(account=pk, name=name).count() != 0:
            raise serializers.ValidationError("Zone name must be unique for account.")
        return name
