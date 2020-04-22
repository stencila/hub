from celery import Celery, signature
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from jobs.models import Job, JobMethod, JobStatus
from projects.models import Project
from users.models import User

# Setup the Celery app
# This is used to send and cancel jobs
celery = Celery("director", broker=settings.BROKER_URL)
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
    }
)


def send_job(queue: str, id: int, method: JobMethod, params: dict):
    """
    Send a job to a queue.

    Constructs a Celery task "signature" and sends it the queue.
    """
    if not JobMethod.is_member(method):
        raise ValueError("Unknown job method '{}'".format(method))
    task = signature(method, kwargs=params, app=celery, queue=queue)
    task.apply_async(kwargs={}, task_id=str(id))


def dispatch_job(job: Job):
    """
    Dispatch a job.

    Decides which queue a job should be sent to and sends it there.
    The queue can depend upon both the project and the account (either the
    account that the project is linked to, or the default account of the job
    creator).
    """
    # TODO: Implement as in docstring
    queue = "stencila"
    send_job(queue, job.id, job.method, job.params)

    # Update the job
    job.queue = queue
    job.status = JobStatus.DISPATCHED.value
    job.save()


@receiver(post_save, sender=Job)
def save_job(sender, instance: Job, created: bool, **kwargs):
    """
    Send a job to the queue when it is created.

    We use the `post_save` signal, because a job may be created
    in the functions below, or in the API, or in the admin interface even.
    In all cases, the job should actually be sent to the queue.
    """
    if created:
        dispatch_job(instance)


# Job creation functions
#
# Not clear if these functions are necessary given the
# API views.
# Currently just define an `execute` job but plan to
# add pull, push, decode, encode, convert, compile, build etc


def execute(user: User, project: Project, params: dict = {}):
    return Job.objects.create(
        creator=user, project=project, method="execute", params=params,
    )


# Job update functions
#
# Update the state of a job
# Currently just `cancel`, but could also involve
# moving a job to another queue (revoke and then re-dispatch).


def cancel(job: Job):
    """
    Cancel a job.

    This uses Celery's terminate options which will kill the worker child process.
    This is not normally recommended but in this case is OK because there is only
    one task per process.
    See `worker/worker.py` for the reasoning for using `SIGUSR1`.
    See https://docs.celeryproject.org/en/stable/userguide/workers.html#revoke-revoking-tasks
    """
    if not JobStatus.is_ready(job.status):
        celery.control.revoke(str(job.id), terminate=True, signal="SIGUSR1")
        job.status = JobStatus.REVOKED.value
        job.ended = timezone.now()
        job.save()
    return job
