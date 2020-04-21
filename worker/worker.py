"""
Stencila Hub Worker.

A Celery app for running jobs.
See https://docs.celeryproject.org/en/latest/userguide/tasks.html.
"""

import asyncio
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from datetime import datetime
import io
import json
import os
import sys
import time

from celery import Celery, states
from celery.exceptions import SoftTimeLimitExceeded
from celery.signals import task_prerun, task_postrun, task_retry
import httpx

from execute.process import ProcessSession


# Setup the Celery app
celery = Celery("worker", broker=os.environ["BROKER_URL"])
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

# Setup API client
api = httpx.Client(
    base_url=os.path.join(os.environ["DIRECTOR_URL"], "api/jobs/"),
    headers={"content-type": "application/json", "accept": "application/json",},
    auth=tuple(os.environ["DIRECTOR_AUTH"].split(":")),
)


def update_job(id, data):
    """
    Update the job.

    Sends a PATCH request to the director that updates the
    state of the job.
    """
    # TODO: Make client an AsyncClient and run this in background
    # asyncio.run(api.patch(...)) doesn't work
    response = api.patch(id, json=data)
    if response.status_code != 200:
        # Generate a warning if not successful
        print(response.json())


@task_prerun.connect
def task_prerun_handler(signal, sender, task_id, task, args, kwargs, **more):
    """
    Dispatched before a task is executed.

    Sender is the task object being executed.
    For a list of available request properties see 
    https://docs.celeryproject.org/en/latest/userguide/tasks.html#task-request.
    """
    update_job(
        task_id,
        {
            "status": states.STARTED,
            "began": datetime.utcnow().isoformat(),
            "queue": task.request.delivery_info["routing_key"],
            "worker": task.request.hostname,
            "retries": task.request.retries,
        },
    )


@task_postrun.connect
def task_postrun_handler(
    signal, sender, task_id, task, args, kwargs, retval, state, **more
):
    """
    Dispatched after a task is executed.

    Sender is the task object being executed.

    When cancelling a job the `director` sends the `SIGUSR1`
    signal which causes a `SoftTimeLimitExceeded` to be thrown.
    See https://github.com/celery/celery/issues/2727 for why
    this is preferable to the `Terminate` signal (which can not
    be caught in the same way and seems to kill the parent worker).
    """
    log = []

    output = task.output if hasattr(task, "output") else ""
    for line in output.split("\n"):
        line = line.strip()
        if len(line) == 0:
            continue
        try:
            entry = json.loads(line)
        except:
            entry = {"message": line}
        log.append(entry)

    if isinstance(retval, SoftTimeLimitExceeded):
        result = None
        state = "TERMINATED"
    elif isinstance(retval, Exception):
        result = None
        log.append(
            {"time": datetime.utcnow().isoformat(), "level": 0, "message": str(retval)}
        )
    else:
        # If the return value can not be JSON stringified then
        # just return it's string representation.
        try:
            json.dumps(retval)
            result = retval
        except:
            result = str(retval)

    update_job(
        task_id,
        {
            "result": result,
            "log": log or None,
            "status": state,
            "ended": datetime.utcnow().isoformat()
        },
    )


@task_retry.connect
def task_retry_handler(**kwargs):
    """
    Dispatched when a task will be retried.

    Sender is the task object.
    """
    print("task_retry_handler", kwargs)


# Celery tasks for each job method


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


@celery.task(name="execute", bind=True, throws=SoftTimeLimitExceeded)
def execute(self):
    try:
        session = ProcessSession()
        update_job(self.request.id, {"url": session.url})
        with capture_output(self):
            session.start()
    except SoftTimeLimitExceeded:
        session.stop()
