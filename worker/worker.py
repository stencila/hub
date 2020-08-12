"""
Stencila Hub Worker.

A Celery app for running jobs.
"""

import os
from typing import Type

from celery import Celery
from kombu import Queue

from jobs.base.job import Job

from jobs.archive import Archive
from jobs.clean import Clean
from jobs.convert import Convert
from jobs.decode import Decode
from jobs.encode import Encode
from jobs.pull import Pull
from jobs.session.session import Session
from jobs.sleep import Sleep

JOBS = [Archive, Clean, Convert, Decode, Encode, Pull, Session, Sleep]

# Setup the Celery app
# If CACHE_URL is not set then falls back to using the RPC backend.
# RPC backend should only be used during development due to it's limitations
# when using multiple `manager` processes.
app = Celery(
    "worker", broker=os.environ["BROKER_URL"], backend=os.getenv("CACHE_URL", "rpc://"),
)
app.conf.update(
    # List of queues to subscribe to
    task_queues=[
        Queue(queue, exchange=queue, routing_key=queue)
        for queue in os.getenv("WORKER_QUEUES", "default").split(",")
    ],
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
    # Disable prefetching
    # By default Celery will prefetch tasks (ie. reserve) from the queue
    # In effect, these tasks sit in the worker's own queue and have state RECEIVED.
    # This can mean that tasks can be blocked by other long running task, even though
    # another worker is available to run them. Setting `task_acks_late = True` avoids this.
    # See:
    #  - https://docs.celeryproject.org/en/stable/userguide/optimizing.html#reserve-one-task-at-a-time
    #  - https://stackoverflow.com/a/37699960/4625911
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


def register(cls: Type[Job]):
    """
    Register a Job.

    The normal way to register a Celery class-based `Task`
    is to use `app.register_task` e.g.

        app.register_task(Pull())

    However, we found that when we did that, that `self.request.id`
    was missing (so although we could send custom events to the
    `overseer` they were useless because they had no task `uuid`).
    See https://github.com/celery/celery/issues/2633 for some
    discussion on this bug (?).

    The following incantations (specifically, using `bind`)
    allow us to get the `request.id` (ie. the `job.id`) and
    pass it on to the `Job` instance.
    """

    @app.task(name=cls.name, base=cls, bind=True)
    def run(self, *args, **kwargs):
        return cls.run(self, *args, **kwargs, task_id=self.request.id)


for job in JOBS:
    register(job)
