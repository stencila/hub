"""
Module that defines the interface between the `manager` (i.e Django) and the `broker` (i.e. RabbitMQ).

Defines three functions involved in a job's lifecycle:

- `dispatch_job` - send a job to a queue
- `update_job` - update the status of a job by checking it's (intermediate) result
- `check_job` - for a parent job, trigger any child jobs, and / or update it's status
- `cancel_job` - remove job from the queue, or terminate it if already started

"""
import datetime
import logging

from celery import Celery, signature
from celery.result import AsyncResult
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from jobs.models import Job, JobMethod, JobStatus, Queue, Worker

logger = logging.getLogger(__name__)

# Setup the Celery app
# This is used to send and cancel jobs
celery = Celery("manager", broker=settings.BROKER_URL, backend="rpc://")
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

    if JobMethod.is_compound(job.method):
        if job.method == JobMethod.parallel.value:
            # Dispatch all child jobs simultaneously
            for child in job.children.all():
                dispatch_job(child)
        else:
            # Dispatch the first child; subsequent children
            # will be status WAITING and will get dispatched later
            # on update of the parent.
            for index, child in enumerate(job.children.all()):
                if index == 0:
                    dispatch_job(child)
                else:
                    child.is_active = True
                    child.status = JobStatus.WAITING.value
                    child.save()

        job.is_active = True
        job.status = JobStatus.DISPATCHED.value
    else:
        # Find queues that have active workers on them
        # order by descending priority
        queues = Queue.objects.filter(
            Q(zone__account=job.project.account) | Q(zone__account__name="stencila"),
            workers__in=Worker.objects.filter(
                # Has not finished
                finished__isnull=True,
                # Has been updated in the last x minutes
                updated__gte=timezone.now() - datetime.timedelta(minutes=15),
            ),
        ).order_by("-priority")

        # Fallback to the default Stencila queue
        # Apart from anything else having this fallback is useful in development
        # because if means that the `overseer` service does not need to be running
        # in order keep track of the numbers of workers listening on each queue
        # (during development `worker`s listen to the default queue)
        if len(queues):
            queue = queues[0]
        else:
            queue, _ = Queue.get_or_create(
                account_name="stencila", queue_name="default"
            )

        # Send the job to the queue
        task = signature(
            job.method,
            kwargs=job.params,
            queue=queue.name,
            task_id=str(job.id),
            app=celery,
        )
        task.apply_async()

        job.queue = queue
        job.is_active = True
        job.status = JobStatus.DISPATCHED.value

    job.save()
    return job


def update_job(job: Job, force: bool = False, update_parent: bool = True) -> Job:
    """
    Update a job based on it's result.

    This method is used to update the status of the job by getting it's
    `AsyncResult`. It is called when (1) the job is retrived (ie. GET) and
    (2) when it is updated with other information (ie PATCH).

    See https://stackoverflow.com/a/38267978 for important considerations
    in using AsyncResult.
    """
    # Avoid unnecessary update
    if not job.is_active and not force:
        return job

    was_active = job.is_active

    # Update the status of compound jobs based on children
    if JobMethod.is_compound(job.method):
        status = job.status
        is_active = False
        previous_succeeded = True
        for child in job.children.all():
            update_job(child, update_parent=False)

            # If the child is active then the compound job is active
            if child.is_active:
                is_active = True

            # If the child has a 'higher' status then update the
            # status of the compound job
            status = JobStatus.highest([status, child.status])

            # If previous children have all succeeded and this child
            # is still waiting then dispatch it.
            if previous_succeeded and child.status == JobStatus.WAITING.value:
                dispatch_job(child)

            if child.status != JobStatus.SUCCESS.value:
                previous_succeeded = False

        job.is_active = is_active
        job.status = JobStatus.RUNNING.value if is_active else status

    # For atomic jobs, get an async result from the backend if the job
    # is not recorded as ready.
    else:
        async_result = AsyncResult(str(job.id), app=celery)
        status = async_result.status
        info = async_result.info

        if status != JobStatus.PENDING.value:
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

        # If the job has a result and no error, then mark it succeeded:
        if job.result is not None and job.error is None:
            job.status = JobStatus.SUCCESS.value

        # If the job has just ended then mark it as inactive
        if JobStatus.has_ended(job.status):
            job.is_active = False

    # If the job is no longer active run it's callback
    if was_active and not job.is_active:
        job.run_callback()

    # If the job has a parent then check it
    if update_parent and job.parent:
        update_job(job.parent)

    job.save()
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
