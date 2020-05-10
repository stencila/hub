"""
Stencila Hub Worker.

A Celery app for running jobs.
See https://docs.celeryproject.org/en/latest/userguide/tasks.html.
"""

from contextlib import contextmanager, redirect_stdout, redirect_stderr
import io
import os

from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded

import session


# Setup the Celery app
celery = Celery("worker", broker=os.environ["BROKER_URL"], backend="rpc://")
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


@contextmanager
def capture_output(task):
    """
    Capture the output of a task.

    Captures both stdout and stderr, concatenates then, and
    sets the `output` property.
    """
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        yield
    task.output = stdout.getvalue() + "\n" + stderr.getvalue()


# Celery tasks for each job method


@celery.task(name="execute", bind=True, throws=SoftTimeLimitExceeded)
def execute(self):
    """
    Execute a node.

    When cancelling a job the `director` sends the `SIGUSR1`
    signal which causes a `SoftTimeLimitExceeded` to be thrown.
    See https://github.com/celery/celery/issues/2727 for why
    this is preferable to the `Terminate` signal (which can not
    be caught in the same way and seems to kill the parent worker).
    """
    try:
        sesh = session.create()
        self.update_state(state="PROGRESS", meta={"url": sesh.url})
        with capture_output(self):
            sesh.start()
    except SoftTimeLimitExceeded:
        sesh.stop()
