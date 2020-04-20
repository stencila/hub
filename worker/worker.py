"""
Stencila Hub Worker.

A Celery app for running jobs.
See https://docs.celeryproject.org/en/latest/userguide/tasks.html.
"""

from contextlib import contextmanager, redirect_stdout, redirect_stderr
from datetime import datetime
import io
import json
import os
import sys
import time

from celery import Celery, states
from celery.signals import task_prerun, task_postrun, task_retry
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Setup the Celery app
app = Celery("worker", broker=os.environ["BROKER_URL"])
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

# Database persistence
#
# Setup the SQLAlchemy database session that is
# used to persist job state to the database.

Model = declarative_base()
engine = create_engine(os.environ["DATABASE_URL"])
Session = sessionmaker(bind=engine, autoflush=False)
session = Session()


class Job(Model):
    """
    SQLAlchemy model for a job.

    This autoloads the schema from the database table
    that is defined by the correspoding Django model.
    """

    __tablename__ = "jobs_job"
    __table_args__ = {"autoload": True, "autoload_with": engine}


def db_save(func):
    """Decorator to commit or rollback the database session within a function."""

    def db_save(*args, **kwargs):
        try:
            func(*args, **kwargs)
            session.commit()
        except Exception:
            session.rollback()
            raise

    return db_save


# Celery task signal handlers
#
# These get run for each task handled by a worker


@task_prerun.connect
@db_save
def task_prerun_handler(signal, sender, task_id, task, args, kwargs, **more):
    """
    Dispatched before a task is executed.

    Sender is the task object being executed.
    For a list of available request properties see 
    https://docs.celeryproject.org/en/latest/userguide/tasks.html#task-request.
    """
    request = task.request
    session.merge(
        Job(
            id=task_id,
            status=states.STARTED,
            began=datetime.utcnow(),
            queue=request.delivery_info["routing_key"],
            worker=request.hostname,
            retries=request.retries,
        )
    )


@task_postrun.connect
@db_save
def task_postrun_handler(
    signal, sender, task_id, task, args, kwargs, retval, state, **more
):
    """
    Dispatched after a task is executed.

    Sender is the task object being executed.
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

    if isinstance(retval, Exception):
        result = None
        log.append(
            {"time": datetime.utcnow().isoformat(), "level": 0, "message": str(retval)}
        )
    else:
        try:
            result = json.dumps(retval)
        except:
            result = json.dumps(str(retval))

    session.merge(
        Job(
            id=task_id,
            result=result,
            log=json.dumps(log) if log else None,
            status=state,
            ended=datetime.utcnow(),
        )
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
    A context manager to capture output of a task.

    Captures both stdout and stderr, concatenates then, and
    sets the `output` property.
    """
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        yield
    task.output = stdout.getvalue() + "\n" + stderr.getvalue()


@app.task(name="execute", bind=True)
def execute(self):
    with capture_output(self):
        print("Hello, I have executed")
