"""
This module defines the interface between the `director` (i.e Django)
and the `broker` (i.e. RabbitMQ). It defines three functions involved in
a job's lifecycle:

- `dispatch_job` - send a job to a queue
- `update_job` - update the status of a job by checking it's (intermediate) result
- `check_job` - for a parent job, trigger any child jobs, and / or update it's status
- `cancel_job` - remove job from the queue, or terminate it if already started

"""
import logging

from celery import Celery, signature
from celery.result import AsyncResult
from django.conf import settings

from jobs.models import Job, JobMethod, JobStatus, Queue

logger = logging.getLogger(__name__)

# Setup the Celery app
# This is used to send and cancel jobs
celery = Celery("director", broker=settings.BROKER_URL, backend="rpc://")
celery.conf.update(
    # By default Celery will keep on trying to connect to the broker forever
    # This overrides that. Initially try again immediately, then add 0.5 seconds for each
    # subsequent try (with a maximum of 3 seconds).
    # See https://github.com/celery/celery/issues/4296
    broker_transport_options={
        "max_retries": 10,
        "interval_start": 0,
        "interval_step": 0.5,
        "interval_max": 3,
    },
    # Needed to ensure STARTED state is emitted
    task_track_started=True,
)


def dispatch_job(job: Job) -> Job:
    """
    Send a job to a queue.

    Decides which queue a job should be sent to and sends it.
    The queue can depend upon both the project and the account (either the
    account that the project is linked to, or the default account of the job
    creator).
    """
    if not JobMethod.is_member(job.method):
        raise ValueError("Unknown job method '{}'".format(job.method))

    if job.method in [JobMethod.series.value, JobMethod.chain.value]:
        # Dispatch the first child; subsequent children
        # will get dispatched via the when the parent is checked
        if job.children:
            dispatch_job(job.children.first())
    elif job.method == JobMethod.parallel.value:
        # Dispatch all child jobs simultaneously
        for child in job.children.all():
            dispatch_job(child)
    else:
        # TODO: Implement as in docstring but using zones (and a default queue per zone)
        queue, _ = Queue.get_or_create(account_name="stencila", queue_name="default")
        job.queue = queue

        # TODO: Send the task to the account's vhost on the broker
        # currently, this just sends to the stencila vhost
        task = signature(
            job.method,
            kwargs=job.params,
            queue=job.queue.name,
            task_id=str(job.id),
            app=celery,
        )
        task.apply_async()

        job.status = JobStatus.DISPATCHED.value

    job.save()
    return job


def update_job(job: Job) -> Job:
    """
    Update a job based on it's result.

    This method is used to update the status of the job by getting it's
    `AsyncResult`. It is called when (1) the job is retrived (ie. GET) and
    (2) when it is updated with other information (ie PATCH).

    See https://stackoverflow.com/a/38267978 for important considerations
    in using AsyncResult.
    """
    # Get an async result from the backend if the job
    # is not recorded as ready.
    if not JobStatus.has_ended(job.status) or job.result is None or job.error is None:
        async_result = AsyncResult(str(job.id), app=celery)
        status = async_result.status
        info = async_result.info

        job.status = status

        if status in [JobStatus.RUNNING.value, JobStatus.SUCCESS.value] and isinstance(
            async_result.info, dict
        ):
            # For RUNNING, `info` is the `meta` kwarg passed to
            # `Job.update_state()` call in the worker process.
            # For SUCCESS, `info` is the value returned
            # by the `Job.success()` method in the worker process.
            for field in ["result", "log", "url"]:
                if field in info:
                    setattr(job, field, info[field])

        if status == JobStatus.FAILURE.value:
            # For FAILURE, `info` is the raised Exception
            job.error = dict(type=type(info).__name__, message=str(info))

        if job.parent is not None:
            check_job(job.parent)

        job.save()
    return job


def check_job(job: Job) -> Job:
    """
    Check a parent job to see if it is finished or if children jobs need to be dispatched.

    TODO: Update the status of the job based on children e.g. if one or more child has failed
    then mark it as failed.
    TODO: if a `series` or `chain` job, then update the next child when the previous
    child has succeeded.
    """
    return job


def cancel_job(job: Job) -> Job:
    """
    Cancel a job.

    This uses Celery's terminate options which will kill the worker child process.
    This is not normally recommended but in this case is OK because there is only
    one task per process.
    See `worker/worker.py` for the reasoning for using `SIGUSR1`.
    See https://docs.celeryproject.org/en/stable/userguide/workers.html#revoke-revoking-tasks
    """
    if not JobStatus.has_ended(job.status):
        celery.control.revoke(str(job.id), terminate=True, signal="SIGUSR1")
        job.status = JobStatus.CANCELLED.value
        job.save()
    return job
