from enum import unique
import json

from django_celery_beat.models import PeriodicTask
from django.core import validators
from django.db import models
from django.utils import timezone
from jsonfallback.fields import FallbackJSONField

from lib.enum_choice import EnumChoice
from accounts.models import Account
from projects.models import Project
from users.models import User


class Zone(models.Model):
    """
    A zone within which jobs are run.

    Zones are similar to, and may correspond with, "availability zones" as
    provided by public providers such as AWS and Google Cloud. Workers
    and the data they operate on are usually colated within zones to
    reduce latency.

    Stencila provides several zones, and users can decide which zone their
    project will run in. Accounts can define their own zones and select those
    for specific projects.
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="zones",
        help_text="The account that this zone is linked to.",
    )

    name = models.CharField(
        max_length=256,
        validators=[
            validators.RegexValidator(
                r"^[a-z][a-z0-9\-]*$",
                "Name should start with a lowercase letter and only contain lowercase letters, digits and hyphens",
            )
        ],
        help_text="The identifier of the queue the job was posted to.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["account", "name"], name="unique_name")
        ]


class Worker(models.Model):
    """
    A worker that runs jobs within a zone.

    This model stores information on a worker as captured by the `overseer` service
    from Celery's worker monitoring events.
    """

    zone = models.ForeignKey(
        Zone,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="workers",
        help_text="The zone that this worker is in.",
    )

    created = models.DateTimeField(
        auto_now_add=True,
        help_text="The time that the worker started (time of the first event for the worker).",
    )

    started = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The time that the worker started (only recorded on a 'worker-online' event).",
    )

    updated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The time that the last heatbeat was received for the worker.",
    )

    finished = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The time that the worker finished (only recorded on a 'worker-offline' event)",
    )

    hostname = models.CharField(
        max_length=512, help_text="The `hostname` of the worker.",
    )

    utcoffset = models.IntegerField(help_text="The `utcoffset` of the worker.",)

    pid = models.IntegerField(help_text="The `pid` of the worker.",)

    freq = models.FloatField(help_text="The worker's heatbeat frequency (in seconds)",)

    software = models.CharField(
        max_length=256, help_text="The name and version of the worker's software.",
    )

    os = models.CharField(
        max_length=64, help_text="Operating system that the worker is running on.",
    )

    signature = models.CharField(
        max_length=512,
        help_text="The signature of the worker used to identify it. "
        "It is possible, but unlikely, that two or more active workers have the same signature.",
    )

    # The number of missing heartbeats before a worker is considered
    # as being inactive
    FLATLINE_HEARTBEATS = 5

    @property
    def active(self):
        return (
            not self.finished
            and (timezone.now() - self.updated).minutes
            < self.freq * Worker.FLATLINE_HEARTBEATS
        )


class WorkerStatus(models.Model):
    """
    The status of a worker at a particular time.

    Stores time varying properties of the worker as available from
    Celery worker monitoring events: `worker_online`, `worker_heartbeat` and `worker_offline`.
    """

    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name="statuses",
        help_text="The worker that this status relates to.",
    )

    time = models.DateTimeField(help_text="The time that this status related to.")

    clock = models.IntegerField(
        help_text="The tick number of the worker's monotonic clock",
    )

    active = models.IntegerField(help_text="The number of active jobs on the worker.",)

    processed = models.IntegerField(
        help_text="The number of jobs that have been processed by the worker.",
    )

    load = FallbackJSONField(
        help_text="An array of the system load over the last 1, 5 and 15 minutes. From os.getloadavg().",
    )


@unique
class JobMethod(EnumChoice):
    """
    An enumeration of available job methods.

    Each job must have one of these methods.
    """

    pull = "pull"
    push = "push"

    decode = "decode"
    encode = "encode"
    convert = "convert"

    compile = "compile"
    build = "build"
    execute = "execute"


@unique
class JobStatus(EnumChoice):
    """
    An enumeration of possible job status.

    These match Celery's "states" with some additions (marked as "custom").
    See https://docs.celeryproject.org/en/stable/reference/celery.states.html
    """

    # Job was sent to a queue (custom).
    DISPATCHED = "DISPATCHED"
    # Job state is unknown.
    PENDING = "PENDING"
    # Job was received by a worker.
    RECEIVED = "RECEIVED"

    # Job was started by a worker.
    STARTED = "STARTED"
    # Job has reported progress since starting (custom).
    PROGRESS = "PROGRESS"
    # Job succeeded
    SUCCESS = "SUCCESS"
    # Job failed
    FAILURE = "FAILURE"

    # Job cancellation message sent (custom).
    CANCELLED = "CANCELLED"
    # Job was revoked.
    REVOKED = "REVOKED"
    # Job was terminated (custom).
    TERMINATED = "TERMINATED"

    # Job was rejected.
    REJECTED = "REJECTED"
    # Job is waiting for retry.
    RETRY = "RETRY"

    @classmethod
    def has_ended(cls, status: str) -> bool:
        return status in [
            member.value
            for member in (
                cls.SUCCESS,
                cls.FAILURE,
                cls.CANCELLED,
                cls.REVOKED,
                cls.TERMINATED,
            )
        ]


class Job(models.Model):
    """
    A job, usually, but not necessarily associated with a project.

    Because some jobs may not be associated with a project, the
    `key` field is a token that provides access to the job outside
    of the usual project permissions.

    If a job is created here in Django, the `creator` field should be
    populated with the current user. Jobs created as part of a pipline
    may not have a creator.

    The fields `method`, `params`, `result` correspond to
    the same properties in [JSON RPC](https://www.jsonrpc.org/specification).

    The `log` field is an array of JSON objects, each corresponding to
    a log entry. Each entry is exected to have a structure of a
    [Logga](https://github.com/stencila/logga) log entry. It will include
    any errors while running the job.

    The fields `queue`, `worker` and `retries` provide for additional
    information on where and how the job was executed.
    """

    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="jobs",
        help_text="The project this job is associated with.",
    )

    creator = models.ForeignKey(
        User,
        null=True,  # Should only be null if the creator is deleted
        blank=True,
        on_delete=models.SET_NULL,
        related_name="jobs_created",
        help_text="The user who created the job.",
    )

    created = models.DateTimeField(
        null=True, auto_now_add=True, help_text="The time the job was created."
    )

    zone = models.ForeignKey(
        Zone,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="jobs",
        help_text="The project this job is associated with.",
    )

    queue = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="The identifier of the queue the job was posted to.",
    )

    began = models.DateTimeField(null=True, help_text="The time the job began.")
    ended = models.DateTimeField(null=True, help_text="The time the job ended.")
    status = models.CharField(
        max_length=32,
        choices=JobStatus.as_choices(),
        blank=True,
        null=True,
        help_text="The current status of the job.",
    )

    method = models.CharField(
        max_length=32, choices=JobMethod.as_choices(), help_text="The job method."
    )
    params = FallbackJSONField(
        blank=True, null=True, help_text="The parameters of the job; a JSON object."
    )
    result = FallbackJSONField(
        blank=True, null=True, help_text="The result of the job; a JSON value."
    )
    log = FallbackJSONField(
        blank=True,
        null=True,
        help_text="The job log; a JSON array of log objects, including any errors.",
    )
    runtime = models.FloatField(
        blank=True, null=True, help_text="The running time of the job."
    )

    # Not a URLField because potential for non-standard schemes e.g. ws://
    url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="The URL of the job on the local network; can be used to interact with it.",
    )

    users = models.ManyToManyField(
        User,
        help_text="The users who have connected to the job; not necessarily currently connected.",
    )

    worker = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="The identifier of the worker that ran the job.",
    )
    retries = models.IntegerField(
        blank=True, null=True, help_text="The number of retries to fulfil the job.",
    )

    @property
    def position(self):
        """
        Position of the job in the queue.

        Counts the number of jobs that were `created` before this
        job and that have no `ended` date.
        """
        return (
            Job.objects.filter(created__lt=self.created, ended__isnull=True).count() + 1
        )


class Pipeline(models.Model):
    """
    A pipeline is a template for one or more jobs.

    Pipelines provide an interface for users to define jobs
    which can then be run on demand, in response to triggers
    (e.g. a push to a repository), or on a schedule.

    Pipelines are not the only way that jobs are created.
    For example, a `convert` job is implicitly created when a user
    uses the "Save as" command.

    Pipelines are superficially similar to continuous integration tools
    like Travis, Github Actions, Azure Pipelines etc but differ
    in that they are focussed on document data flows, including pulling
    and pushing documents from/to alternative sources.

    A pipeline's definition is stored as JSON but can be authored
    by users using YAML or a GUI.
    """

    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="pipelines",
        help_text="The project this pipeline is linked to.",
    )

    name = models.SlugField(
        max_length=256,
        help_text="A name for this pipeline. Must be unique to the project.",
    )

    definition = FallbackJSONField(help_text="The JSON definition of the pipeline.")

    schedule = models.OneToOneField(
        "PipelineSchedule",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="pipeline",
        help_text="The schedule for this pipeline.",
    )

    def save(self, *args, **kwargs):
        """
        Override save to set necessary fields for the schedule.

        The `pipeline` task must be defined in workers and take
        a `definition` argument that will be transformed into a
        jobs and run on the worker.
        """
        if self.schedule:
            self.schedule.name = "Pipeline {} schedule".format(self.name)
            self.schedule.task = "pipeline"
            self.schedule.kwargs = json.dumps(dict(definition=self.definition))
            # TODO Choose a queue based on the project
            self.schedule.queue = "stencila"
            self.schedule.save()
        return super().save(*args, **kwargs)


class PipelineSchedule(PeriodicTask):
    """
    A schedule that defines when a pipeline should be run.

    This model currently does not extend django_celery_beat's
    `PeriodicTask` with any new fields, but is a sublass in
    case we want to do that in the future.
    """

    pass
