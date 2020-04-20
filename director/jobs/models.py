from enum import unique
from django.db import models
from jsonfallback.fields import FallbackJSONField

from lib.enum_choice import EnumChoice
from projects.models import Project
from users.models import User


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

    These match Celery's "states". See
    https://docs.celeryproject.org/en/stable/reference/celery.states.html
    """

    # Task state is unknown.
    PENDING = "PENDING"
    # Task was received by a worker.
    RECEIVED = "RECEIVED"
    # Task was started by a worker.
    STARTED = "STARTED"
    # Task succeeded
    SUCCESS = "SUCCESS"
    # Task failed
    FAILURE = "FAILURE"
    # Task was revoked.
    REVOKED = "REVOKED"
    # Task was rejected.
    REJECTED = "REJECTED"
    # Task is waiting for retry.
    RETRY = "RETRY"

    @classmethod
    def is_ready(cls, status: str) -> bool:
        return status in [
            member.value for member in (cls.SUCCESS, cls.FAILURE, cls.REVOKED)
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
        on_delete=models.SET_NULL,
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

    began = models.DateTimeField(null=True, help_text="The time the job began.")
    ended = models.DateTimeField(null=True, help_text="The time the job ended.")
    status = models.CharField(
        max_length=32,
        choices=JobStatus.as_choices(),
        blank=True,
        null=True,
        help_text="The current status of tje job.",
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

    queue = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="The identifier of the queue the job was posted to.",
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

    WIP
    """

    class Meta:
        abstract = True

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="pipelines",
        help_text="The project this pipeline is associated with.",
    )

    definition = FallbackJSONField(help_text="The JSON definition of the pipeline.")

    schedule = models.ForeignKey(
        "Schedule",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The schedule on which the pipeline will be executed.",
    )


class Schedule(models.Model):
    """
    A schedule defines when a pipeline should be executed.

    WIP
    """

    class Meta:
        abstract = True
