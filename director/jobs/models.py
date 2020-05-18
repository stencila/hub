from enum import unique
import json
import re

from django_celery_beat.models import PeriodicTask
from django.core import validators
from django.db import models
from django.utils import timezone
from jsonfallback.fields import FallbackJSONField

from lib.enum_choice import EnumChoice
from accounts.models import Account
from users.models import User


class Zone(models.Model):
    """
    A zone within which jobs are run and data is stored.

    A zone is really just a label for where to put data and
    run jobs so that they can be colated to reduce latency.
    They are similar to, and may correspond with, "availability zones" as
    provided by public cloud providers such as AWS and Google Cloud.
    A zone could also simply be a laptop in someone's bedroom.

    Zones are linked to accounts. The Stencila account provides several zones,
    and users can decide which zone their project will run in.
    Other zccounts can define their own zones and select those for specific
    projects.
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


class Queue(models.Model):
    """
    A queue upon which jobs are placed.

    Queues are always associated with a zone. They have several attributes
    that determine which jobs are placed on them:

    - priority: the relative priority of jobs on the queue
    - untrusted: whether or not jobs on the queue can execute untrusted code
    - interrupt: whether or not jobs on the queue can be interrupted

    Queues are implicitly created when a worker comes online
    and declares which queues it is listening to. The attributes
    of a queue are defined by it's name, using the format:

        <zone>[:priority][:untrusted][:interrupt]

    For example, a Celery worker might be started like this:

        celery -A proj worker -Q north-1:untrusted --concurrency 100

    meaning that it will run up to 100 concurrent, untrusted, uninterruptible
    (the default) jobs of priority 1.

    That is, queues are created by workers (rather than having to be predefined and
    workers subscribing to them). This "inversion of control" is counter to
    how one might first think of the relationship between workers and queues.
    """

    NAME_REGEX = r"^([a-z][a-z0-9\-]*)(:[0-9])?(:untrusted)?(:interrupt)?$"

    name = models.CharField(max_length=512, help_text="The name of the queue.")

    zone = models.ForeignKey(
        Zone,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="jobs",
        help_text="The zone this job is associated with.",
    )

    priority = models.IntegerField(
        default=0, help_text="The relative priority of jobs placed on the queue."
    )

    untrusted = models.BooleanField(
        default=False,
        help_text="Whether or not the queue should be sent jobs which run untrusted code.",
    )

    interrupt = models.BooleanField(
        default=False,
        help_text="Whether or not the queue should be sent jobs which can not be interupted."
        "False (default): jobs should not be interrupted",
    )

    @classmethod
    def get_or_create(cls, account_name, queue_name):
        """
        Get or create a queue from a name and account name.

        This method extracts the fields of a queue model from two strings
        obtained from Celery when a worker comes online:

        - name = the name of the queue
        - account_name = the broker vhost that the worker if listening to

        If there is already a queue with the name (for the account) then
        it will be returned. Otherwise, a new queue wll be created.
        """
        match = re.search(cls.NAME_REGEX, queue_name)
        assert match is not None

        account = Account.objects.get(name=account_name)
        zone, created = Zone.objects.get_or_create(account=account, name=match.group(1))

        priority = match.group(2)
        priority = int(priority[1:]) if priority else 0

        untrusted = match.group(3) is not None
        interrupt = match.group(4) is not None

        return cls.objects.get_or_create(
            name=queue_name,
            zone=zone,
            priority=priority,
            untrusted=untrusted,
            interrupt=interrupt,
        )


class Worker(models.Model):
    """
    A worker that runs jobs placed on one or more queues.

    This model stores information on a worker as captured by the `overseer` service
    from Celery's worker monitoring events.
    """

    queues = models.ManyToManyField(
        Queue,
        related_name="workers",
        help_text="The queues that this worker is listening to.",
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

    details = FallbackJSONField(
        null=True,
        blank=True,
        help_text="Details about the worker including queues and stats"
        "See https://docs.celeryproject.org/en/stable/userguide/workers.html#statistics",
    )

    signature = models.CharField(
        max_length=512,
        help_text="The signature of the worker used to identify it. "
        "It is possible, but unlikely, that two or more active workers have the same signature.",
    )

    # The number of missing heartbeats before a worker is considered
    # as being inactive
    FLATLINE_HEARTBEATS = 5

    @classmethod
    def get_or_create(cls, event: dict, create=False):
        """
        Get or create a worker from a Celery worker event.

        This method extracts the fields of a worker from a
        Celery worker event and constructs a signature from them.
        If there is an active worker with the same signature then
        it is returned.

        The signature is the only way to uniquely identify
        a worker.
        """
        hostname = event.get("hostname")
        utcoffset = event.get("utcoffset")
        pid = event.get("pid")
        freq = event.get("freq")
        software = "{}-{}".format(event.get("sw_ident"), event.get("sw_ver"))
        os = event.get("sw_sys")
        details = event.get("details", {})

        signature = "{hostname}|{utcoffset}|{pid}|{freq}|{software}|{os}".format(
            hostname=hostname,
            utcoffset=utcoffset,
            pid=pid,
            freq=freq,
            software=software,
            os=os,
        )

        if not create:
            try:
                return Worker.objects.get(signature=signature, finished__isnull=True)
            except Worker.DoesNotExist:
                pass

        return Worker.objects.create(
            hostname=hostname,
            utcoffset=utcoffset,
            pid=pid,
            freq=freq,
            software=software,
            os=os,
            details=details,
            signature=signature,
        )

    @property
    def active(self):
        """Is the worker still active."""
        if self.finished:
            return False
        if self.updated:
            return (
                timezone.now() - self.updated
            ).minutes < self.freq * Worker.FLATLINE_HEARTBEATS
        return True


class WorkerHeartbeat(models.Model):
    """
    A worker heartbeat event.

    Stores time varying properties of the worker as available from
    Celery worker monitoring events. The names of the fields of this model
    are intended to be consistent with those.
    See https://docs.celeryproject.org/en/stable/userguide/monitoring.html#worker-events
    """

    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name="heartbeats",
        help_text="The worker that the heartbeat is for.",
    )

    time = models.DateTimeField(help_text="The time of the heartbeat.")

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

    parallel = "parallel"
    series = "series"
    chain = "chain"

    pull = "pull"
    push = "push"

    decode = "decode"
    encode = "encode"
    convert = "convert"

    compile = "compile"
    build = "build"
    execute = "execute"

    session = "session"

    sleep = "sleep"


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
    # Job is running (custom).
    RUNNING = "RUNNING"
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

    @classmethod
    def icon(cls, status: str) -> str:
        """Assign the correct icon to use based on the status."""
        icon = "loader"
        icon = "play-circle" if status == cls.STARTED.value else icon
        icon = "check-circle" if status == cls.SUCCESS.value else icon
        icon = (
            "x-octagon"
            if status
            in [member.value for member in (cls.FAILURE, cls.REJECTED, cls.REVOKED,)]
            else icon
        )
        icon = (
            "slash"
            if status in [member.value for member in (cls.CANCELLED, cls.TERMINATED,)]
            else icon
        )
        icon = "rotate-cw" if status == cls.RETRY.value else icon

        return icon

    @classmethod
    def colour(cls, status: str) -> str:
        """Assign the correct colour to use based on the status."""
        icon = "info"
        icon = "success" if status == cls.SUCCESS.value else icon
        icon = (
            "danger"
            if status
            in [member.value for member in (cls.FAILURE, cls.REJECTED, cls.REVOKED,)]
            else icon
        )
        icon = (
            "grey-light"
            if status in [member.value for member in (cls.CANCELLED, cls.TERMINATED,)]
            else icon
        )
        icon = "warning" if status == cls.RETRY.value else icon

        return icon


class Job(models.Model):
    """
    A job, usually, but not necessarily associated with a project.

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
        "projects.Project",
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

    queue = models.ForeignKey(
        Queue,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="jobs",
        help_text="The queue that this job was routed to",
    )

    parent = models.ForeignKey(
        "Job",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        help_text="The parent job",
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
    error = FallbackJSONField(
        blank=True,
        null=True,
        help_text="Any error associated with the job; a JSON object with type, message etc.",
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

    @property
    def get_runtime(self):
        """
        Format the runtime into a format that can be printed to the screen.

        i.e. convert from float into hours:mins format.
        """
        if self.began is not None and self.ended is not None:
            difference = self.ended - self.began
            seconds = difference.total_seconds()

            h = seconds // 3600
            m = (seconds % 3600) // 60

            return "%d:%d" % (h, m)

        return None

    @property
    def icon(self):
        """Get the icon from the status - used in the template."""
        return JobStatus.icon(self.status)

    @property
    def colour(self):
        """Get the colour from the status - used in the template."""
        return "is-{}".format(JobStatus.colour(self.status))

    @property
    def status_label(self):
        """Get a printable version of the status - used in the template."""
        inQueue = self.queue is None
        status = JobStatus[self.status]
        label = status.value
        label = (
            "Pending"
            if status.value == JobStatus.PENDING.value and not inQueue
            else label
        )
        label = (
            "In Queue" if status.value == JobStatus.PENDING.value and inQueue else label
        )

        return label

    @property
    def has_ended(self):
        """Check if the status is one of the defined ended statuses."""
        return JobStatus.has_ended(self.status)

    # Shortcuts to the functions for controlling
    # and updating jobs.
    def dispatch(self) -> "Job":
        from jobs.jobs import dispatch_job

        return dispatch_job(self)

    def update(self) -> "Job":
        from jobs.jobs import update_job

        return update_job(self)

    def cancel(self) -> "Job":
        from jobs.jobs import catch_job

        return catch_job(self)


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
        "projects.Project",
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
