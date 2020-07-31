"""
Stencila Hub Worker.

A Celery app for running jobs.
"""

import os
from typing import Type

from celery import Celery

from jobs.base.job import Job

from jobs.archive import Archive
from jobs.clean import Clean
from jobs.convert import Convert
from jobs.decode import Decode
from jobs.encode import Encode
from jobs.pull import Pull
from jobs.session import Session
from jobs.sleep import Sleep

JOBS = [Archive, Clean, Convert, Decode, Encode, Pull, Session, Sleep]


# Setup the Celery app
app = Celery("worker", broker=os.environ["BROKER_URL"], backend="rpc://")
app.conf.update(
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


def register(cls: Type[Job]):
    """
    Register a Job.

    The normal way to register a Celery class-based `Task`
    is to use `app.register_task` e.g.
    
        app.register_task(Pull())

    However, we found that when we did that, that `self.request.id
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
