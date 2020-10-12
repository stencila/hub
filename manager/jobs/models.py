import json
import re
from enum import unique
from typing import List, Optional

import inflect
import shortuuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import ordinal
from django.core import validators
from django.db import models, transaction
from django.http import HttpRequest
from django.utils import timezone
from django.utils.functional import cached_property
from django_celery_beat.models import PeriodicTask

from accounts.models import Account
from manager.helpers import EnumChoice
from users.models import AnonUser, User


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

    def __str__(self) -> str:
        return "Zone #{0}:{1}".format(self.id, self.name)


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

    def __str__(self):
        return "Queue #{0}:{1}".format(self.id, self.name)

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

    utcoffset = models.IntegerField(
        null=True, blank=True, help_text="The `utcoffset` of the worker.",
    )

    pid = models.IntegerField(
        null=True, blank=True, help_text="The `pid` of the worker.",
    )

    freq = models.FloatField(
        null=True, blank=True, help_text="The worker's heatbeat frequency (in seconds)",
    )

    software = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="The name and version of the worker's software.",
    )

    os = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Operating system that the worker is running on.",
    )

    details = models.JSONField(
        null=True,
        blank=True,
        help_text="Details about the worker including queues and stats"
        "See https://docs.celeryproject.org/en/stable/userguide/workers.html#statistics",
    )

    signature = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text="The signature of the worker used to identify it. "
        "It is possible, but unlikely, that two or more active workers have the same signature.",
    )

    # The number of missing heartbeats before a worker is considered
    # as being inactive
    FLATLINE_HEARTBEATS = 5

    @classmethod
    @transaction.atomic
    def get_or_create(cls, event: dict, create=False):
        """
        Get or create a worker from a Celery worker event.

        This method extracts the fields of a worker from a
        Celery worker event and constructs a signature from them.
        If there is an active worker with the same signature then
        it is returned.

        The signature is the only way to uniquely identify
        a worker.

        Atomic to avoid race conditions creating two workers with the
        same signature.
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
            return (timezone.now() - self.updated).seconds < (
                self.freq * Worker.FLATLINE_HEARTBEATS
            )
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

    load = models.JSONField(
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

    clean = "clean"
    archive = "archive"

    pull = "pull"
    push = "push"

    decode = "decode"
    encode = "encode"
    convert = "convert"

    pin = "pin"

    compile = "compile"
    build = "build"
    execute = "execute"

    session = "session"

    sleep = "sleep"

    @classmethod
    def is_compound(cls, method: str) -> bool:
        """Is this a compound job method."""
        return method in [
            member.value for member in (cls.parallel, cls.series, cls.chain)
        ]


@unique
class JobStatus(EnumChoice):
    """
    An enumeration of possible job status.

    These match Celery's "states" with some additions (marked as "custom").
    See https://docs.celeryproject.org/en/stable/reference/celery.states.html
    """

    # Job is awaiting another job
    WAITING = "WAITING"

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
    # Job was revoked (cancelled before it was started).
    REVOKED = "REVOKED"
    # Job was terminated (started and then cancelled, custom).
    TERMINATED = "TERMINATED"

    # Job was rejected.
    REJECTED = "REJECTED"
    # Job is waiting for retry.
    RETRY = "RETRY"

    @classmethod
    def has_ended(cls, status: str) -> bool:
        """Has the job ended."""
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
    def rank(cls, status: str) -> int:
        """
        Get the rank of a status.

        Ranks broadly reflect the order in which statuses will
        change on a job.
        """
        return {
            "WAITING": 0,
            "DISPATCHED": 1,
            "PENDING": 2,
            "RECEIVED": 3,
            "STARTED": 4,
            "RUNNING": 5,
            "SUCCESS": 6,
            "CANCELLED": 7,
            "REVOKED": 8,
            "TERMINATED": 9,
            # Failure is highest rank because
            # compound jobs should have FAILURE if any
            # children are failed.
            "FAILURE": 10,
        }.get(status, 0)

    @classmethod
    def highest(cls, statuses: List[str]) -> str:
        """
        Get the status which has the highest rank.
        """
        ranks = [JobStatus.rank(status) for status in statuses]
        max_rank = max(ranks)
        max_index = ranks.index(max_rank)
        return statuses[max_index]

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


def generate_job_id():
    """
    Generate a unique job id.

    The is separate function to avoid new AlterField migrations
    being created as happens when `default=shortuuid.uuid`.

    Not currently used, but retained so that migrations continue
    to work.
    """
    return shortuuid.uuid()


def generate_job_key():
    """
    Generate a unique, and very difficult to guess, job key.
    """
    return shortuuid.ShortUUID().random(length=32)


class Job(models.Model):
    """
    A job, usually, but not necessarily associated with a project.

    The `creator` field should be populated with the current user.
    Jobs created as part of a pipline, or by an anonymous user, may not have a creator.

    The `key` field provides a way of accessing the job instead of using
    the easy-to-guess `id`.

    The `description` can be used to provide the user with a summary of
    what the job is doing.

    The fields `method`, `params`, `result` correspond to
    the same properties in [JSON RPC](https://www.jsonrpc.org/specification).

    The `log` field is an array of JSON objects, each corresponding to
    a log entry. Each entry is exected to have a structure of a
    [Logga](https://github.com/stencila/logga) log entry. It will include
    any errors while running the job.

    The fields `queue`, `worker` and `retries` provide for additional
    information on where and how the job was executed.
    """

    id = models.BigAutoField(
        primary_key=True,
        help_text="An autoincrementing integer to allow selecting jobs in the order they were created.",
    )

    key = models.CharField(
        default=generate_job_key,
        max_length=64,
        help_text="A unique, and very difficult to guess, key to access the job with.",
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="A short description of the job.",  # See property `summary_string`
    )

    project = models.ForeignKey(
        "projects.Project",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="jobs",
        help_text="The project this job is associated with.",
    )

    snapshot = models.ForeignKey(
        "projects.Snapshot",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="jobs",
        help_text="The snapshot that this job is associated with. "
        "Usually `session` jobs for the snapshot.",
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
        auto_now_add=True, help_text="The time the job was created."
    )

    updated = models.DateTimeField(
        auto_now=True, help_text="The time the job was last updated."
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

    began = models.DateTimeField(
        null=True, blank=True, help_text="The time the job began."
    )
    ended = models.DateTimeField(
        null=True, blank=True, help_text="The time the job ended."
    )

    status = models.CharField(
        max_length=32,
        choices=JobStatus.as_choices(),
        null=True,
        blank=True,
        help_text="The current status of the job.",
    )

    is_active = models.BooleanField(
        default=False, db_index=True, help_text="Is the job active?",
    )

    method = models.CharField(
        max_length=32, choices=JobMethod.as_choices(), help_text="The job method."
    )
    params = models.JSONField(
        null=True, blank=True, help_text="The parameters of the job; a JSON object."
    )
    result = models.JSONField(
        null=True, blank=True, help_text="The result of the job; a JSON value."
    )
    error = models.JSONField(
        null=True,
        blank=True,
        help_text="Any error associated with the job; a JSON object with type, message etc.",
    )

    log = models.JSONField(
        null=True,
        blank=True,
        help_text="The job log; a JSON array of log objects, including any errors.",
    )
    runtime = models.FloatField(
        null=True, blank=True, help_text="The running time of the job."
    )

    # Not a URLField because potential for non-standard schemes e.g. ws://
    url = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="The URL of the job on the local network; can be used to interact with it.",
    )

    users = models.ManyToManyField(
        User,
        blank=True,
        help_text="Users who have created or connected to the job; not necessarily currently connected.",
    )

    anon_users = models.ManyToManyField(
        AnonUser,
        blank=True,
        help_text="Anonymous users who have created or connected to the job.",
    )

    worker = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="The identifier of the worker that ran the job.",
    )

    retries = models.IntegerField(
        null=True, blank=True, help_text="The number of retries to fulfil the job.",
    )

    callback_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="The type of the object to call back.",
    )

    callback_id = models.CharField(
        null=True,
        blank=True,
        max_length=256,
        help_text="The id of the object to call back.",
    )

    callback_method = models.CharField(
        null=True,
        blank=True,
        max_length=128,
        help_text="The name of the method to call back.",
    )

    callback_object = GenericForeignKey("callback_type", "callback_id")

    @cached_property
    def status_message(self) -> str:
        """
        Generate a message for users describing the status of the job.
        """
        subject = "Session" if self.method == JobMethod.session.value else self.method
        if self.status == JobStatus.DISPATCHED.value:
            message = "{subject} is {position} in the queue.".format(
                subject=subject, position=ordinal(self.position)
            )
            return message
        elif self.status == JobStatus.RECEIVED.value:
            return "{subject} is starting.".format(subject=subject)
        elif self.status == JobStatus.STARTED.value:
            if self.method == JobMethod.session.value:
                # Sessions can take some time between `STARTED` and
                # `RUNNING`. e.g. to pull images etc. So report these
                # as "is starting" still.
                return "Session is starting"
            else:
                # Many jobs do not emit a `RUNNING` state so
                # report these as "has started"
                return "{subject} has started.".format(subject=subject)
        elif self.status == JobStatus.RUNNING.value:
            return "{subject} is running.".format(subject=subject)
        elif self.status == JobStatus.SUCCESS.value:
            return "{subject} has finished.".format(subject=subject)
        elif self.status == JobStatus.FAILURE.value:
            return "{subject} has failed.".format(subject=subject)
        elif self.status in [
            JobStatus.CANCELLED.value,
            JobStatus.REVOKED.value,
            JobStatus.TERMINATED.value,
        ]:
            return "{subject} was cancelled.".format(subject=subject)
        else:
            return "{subject} is {status}.".format(
                subject=subject, status=self.status.lower()
            )

    @cached_property
    def summary_string(self) -> str:
        """
        Get a short textual summary of the job.

        Intended for user interfaces.
        If the `description` field is not set then will be derived from
        the job's `method` and `params` fields.
        """
        if self.description:
            return self.description

        method = self.method
        params = self.params

        summary = method.title()
        if method == "pull":
            path = params and params["path"]
            summary += " '{0}'".format(path)

        return summary

    @cached_property
    def position(self):
        """
        Position of the job in the queue.

        Counts the number of jobs that were `created` before this
        job and that have no `ended` date.
        """
        return (
            Job.objects.filter(
                queue=self.queue,
                created__lt=self.created,
                status=JobStatus.DISPATCHED.value,
            ).count()
            + 1
        )

    @cached_property
    def runtime_seconds(self) -> float:
        """
        Get the runtime in seconds.
        """
        if self.runtime is not None:
            return self.runtime
        elif self.began and self.ended:
            return (self.ended - self.began).seconds
        else:
            return (timezone.now() - self.created).seconds

    @cached_property
    def runtime_formatted(self) -> Optional[str]:
        """
        Format the runtime into a format that can be printed to the screen.

        i.e. convert from float into hours:mins format.
        It follows the following rules:
        - If the job has not started, return empty string
        - If job has started & not ended calculate time relative to now.
        - If job has ended, calculate difference.
        """
        runtime = self.runtime_seconds
        h, rem = divmod(runtime, 3600)
        m, s = divmod(rem, 60)

        if h == 0 and m == 0 and s == 0:
            return "<1 sec"

        p = inflect.engine()
        output = [
            "%d %s" % (h, p.plural("hour", h)) if h != 0 else "",
            "%d %s" % (m, p.plural("min", m)) if m != 0 else "",
            "%d %s" % (s, p.plural("sec", s)) if s != 0 else "",
        ]
        return " ".join(x for x in output).strip()

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
        if self.status is None:
            # TODO: If there is no status, assume it's dispatched?
            # self.status = JobStatus.DISPATCHED.name
            return None

        status = JobStatus[self.status]

        return status.value

    @property
    def has_ended(self):
        """Check if the status is one of the defined ended statuses."""
        return JobStatus.has_ended(self.status)

    def result_prettified(self):
        """Prettify the JSON result, if any."""
        return json.dumps(self.result, indent="  ") if self.result else None

    def get_children(self) -> models.QuerySet:
        """Get the child jobs of this job in order of id."""
        return self.children.all().order_by("id")

    # Shortcuts to the functions for controlling
    # and updating jobs.

    def dispatch(self) -> "Job":
        """Dispatch the job."""
        from jobs.jobs import dispatch_job

        return dispatch_job(self)

    def update(self, *args, **kwargs) -> "Job":
        """Update the job."""
        from jobs.jobs import update_job

        return update_job(self, *args, **kwargs)

    def cancel(self) -> "Job":
        """Cancel the job."""
        from jobs.jobs import cancel_job

        return cancel_job(self)

    # Methods for registering and running callbacks

    @staticmethod
    def create_callback(model: models.Model, method: str):
        """
        Create a dictionary of callback fields.

        A shortcut for use when creating a job.
        """
        return dict(
            callback_type=ContentType.objects.get_for_model(model),
            callback_id=model.id,
            callback_method=method,
        )

    def run_callback(self):
        """
        If a callback was registered on job creation then run it.
        """
        if self.callback_type:
            if self.callback_id and self.callback_method:
                obj = self.callback_object
                if obj:
                    func = getattr(obj, self.callback_method)
                    func(self)

    def add_user(self, request: HttpRequest):
        """
        Add the request user to the job.

        If the user is authenticated, they are added to
        `users`, otherwise to `anon_users`.
        """
        if request.user.is_authenticated:
            self.users.add(request.user)
        else:
            anon_user = AnonUser.get_or_create(request)
            self.anon_users.add(anon_user)


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

    definition = models.JSONField(help_text="The JSON definition of the pipeline.")

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
