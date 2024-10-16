import logging
import re

from django.conf import settings
from django.shortcuts import reverse
from rest_framework import serializers

from accounts.models import Account
from jobs.models import Job, JobMethod, Queue, Worker, WorkerHeartbeat, Zone
from manager.api.helpers import get_object_from_ident
from manager.api.validators import FromContextDefault
from projects.models.projects import Project

logger = logging.getLogger(__name__)


class JobListSerializer(serializers.ModelSerializer):
    """
    A job serializer for the `list` action.

    This serializer includes all model fields except potentially
    large JSON fields.
    Some are made read only in derived serializers
    (e.g. can not be set in `create` or `update` views).

    Also adds "cheap to calculate" properties derived from other
    fields. e.g. `summary_string`
    """

    status_message = serializers.CharField(read_only=True)

    summary_string = serializers.CharField(read_only=True)

    runtime_formatted = serializers.CharField(read_only=True)

    urls = serializers.SerializerMethodField()

    url = serializers.SerializerMethodField()

    class Meta:
        model = Job
        exclude = ["params", "result", "error", "log", "secrets"]

    def get_urls(self, job: Job):
        """
        Get the URLs to connect to the job from outside the local network.

        A map of protocols to URLs e.g.

        ```json
        "urls": {
          "http": "https://hub.stenci.la/api/projects/1/jobs/16/connect?key=DYBnucbz8ZQC7xKsgEPL5Vm26oTfvZvg",
          "ws": "wss://hub.stenci.la/api/projects/1/jobs/16/connect?key=DYBnucbz8ZQC7xKsgEPL5Vm26oTfvZvg"
        },
        ```

        Will be `null` if the job does not have any internal URLs or has ended.
        """
        if job.urls and job.is_active:
            if settings.JOB_URLS_LOCAL:
                return job.urls
            else:
                request = self.context.get("request")
                urls = {}
                for protocol, url in job.urls.items():
                    # Get the URL that gives (and records) access to the job
                    url = request.build_absolute_uri(
                        reverse(
                            "api-projects-jobs-connect",
                            kwargs=dict(project=job.project.id, job=job.id),
                        )
                        + f"?protocol={protocol}&key={job.key}"
                    )

                    # The `build_absolute_uri` function will always return
                    # `http` or `https` so replace with the protocol of the URL if necessary.
                    # Note: this will result a `wss://` URL if the request is a secure one (i.e. HTTPS).
                    if protocol == "ws":
                        url = re.sub(r"^http", "ws", url)

                    urls[protocol] = url

            return urls

    def get_url(self, job: Job):
        """
        Get the Websocket URL of the job.

        This field is deprecated, use `urls` instead. It is provided for
        backwards compatability with previous API versions and may be removed
        in the future.
        """
        urls = self.get_urls(job)
        return urls.get("ws") if urls else None


class JobRetrieveSerializer(JobListSerializer):
    """
    A job serializer for the `retrieve` action.

    Adds all fields as well as the `position` of the job in the
    queue (which involves another database query for each job
    so is probably best to avoid for jobs in a list).
    """

    position = serializers.IntegerField(read_only=True)

    children = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    params = serializers.SerializerMethodField()

    class Meta:
        model = Job
        exclude = ["secrets"]

    def get_params(self, job: Job):
        """
        Remove `secrets` from the job's parameters (if present).

        Removes any secrets in the job parameters.
        Secrets should not be placed in job parameters in the first case.
        This is a further precaution to avoid leakage if they are present
        and as such logs a warning if they are.
        """
        if job.params and "secrets" in job.params:
            logger.warning("Secrets were present in job params", extra={"job": job.id})
            del job.params["secrets"]
        return job.params


class JobCreateSerializer(JobRetrieveSerializer):
    """
    A job serializer for the `create` action.

    Makes most fields readonly (ie. can not be set),
    makes some fields required.
    """

    class Meta:
        model = Job
        exclude = ["secrets"]
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
            "urls",
            "log",
            "runtime",
            "users",
            "retries",
            "worker",
        ]

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
        exclude = ["secrets"]
        read_only_fields = ["creator", "created", "method", "params", "zone", "queue"]


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
