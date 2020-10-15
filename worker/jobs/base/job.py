import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import celery
import sentry_sdk
from celery import states
from celery.exceptions import Ignore, SoftTimeLimitExceeded
from celery.utils.log import get_task_logger
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from config import get_working_dir

# Log levels
# These are the same as used in https://github.com/stencila/logga
ERROR = 0
WARN = 1
INFO = 2
DEBUG = 3

# Get the Celery logger
logger = get_task_logger(__name__)

# Initialize Sentry. This reuses the environment variable already set
# for the `manager` service (which is why it is prefixed by `DJANGO_`).
DJANGO_SENTRY_DSN = os.environ.get("DJANGO_SENTRY_DSN")
if DJANGO_SENTRY_DSN:
    sentry_sdk.init(
        dsn=DJANGO_SENTRY_DSN, integrations=[CeleryIntegration(), RedisIntegration()]
    )
else:
    logger.warning(
        "No DJANGO_SENTRY_DSN environment variable, errors will not be reported to Sentry."
    )


class Job(celery.Task):
    """
    Base class for all Jobs.

    Extends Celery's Task class to handle logging and
    termination of jobs.
    """

    def begin(self, task_id=None):
        """
        Begin the job.

        Because the `run()` method is executed several times
        for each task instance, this method performs any
        initialization in advance.
        """
        self.task_id = task_id
        self.log_entries = []

    def notify(self, state="RUNNING", **kwargs):
        """
        Send a notification to the `overseer` service.

        Used to update the status, url, log etc of a job.
        """
        if self.task_id:
            self.send_event(
                "task-updated", task_id=self.task_id, state=state, **kwargs,
            )

    def flush(self):
        """
        Flush the log.

        In the future this may be more intelligent and buffer
        sending of log events to reduce the number
        of requests.
        """
        if len(self.log_entries):
            self.notify(log=self.log_entries)

    def log(self, level: int, message: str):
        """
        Create a log entry.

        This function:

        - Emits to the Python logger, and

        - Appends an entry to the job's log and updates the
          state with the log as metadata thereby making the
          log and any extra details available to the `manager`.
          (see the `update_job` there for how these are extracted)
        """
        log_message = "Job {0}: {1}".format(self.name, message)
        log_extra = {"task_id": self.task_id, "job_method": self.name}
        if level == DEBUG:
            logger.debug(log_message, extra=log_extra)
        elif level == INFO:
            logger.info(log_message, extra=log_extra)
        elif level == WARN:
            logger.warning(log_message, extra=log_extra)
        else:
            logger.error(log_message, extra=log_extra)

        self.log_entries.append(
            dict(time=datetime.utcnow().isoformat(), level=level, message=message)
        )
        self.flush()

    def error(self, message: str):
        """Log an error message."""
        self.log(ERROR, message)

    def warn(self, message: str):
        """Log a warning message."""
        self.log(WARN, message)

    def info(self, message: str):
        """Log a informational message."""
        self.log(INFO, message)

    def debug(self, message: str):
        """Log a debug message."""
        self.log(DEBUG, message)

    def success(self, result: Any):
        """
        Job has succeeded.

        This method bundles the job result and the log together
        and returns them both as the Celery task result.
        """
        return dict(result=result, log=self.log_entries)

    def terminated(self):
        """
        Job has been terminated.

        When cancelling a job the `manager` sends the `SIGUSR1`
        signal which causes a `SoftTimeLimitExceeded` to be thrown
        and this method to be called.

        See https://github.com/celery/celery/issues/2727 for why
        this is preferable to the `Terminate` signal (which can not
        be caught in the same way and seems to kill the parent worker).

        This method just flushes the log.
        """
        self.flush()

    def failure(self, exc: Exception):
        """
        Job has failed due to an exception.

        This method re-raises the exception so that it can be handled
        by Celery (e.g. the job marked with `FAILURE`). However, before
        doing so it reports the error to Sentry.
        """
        sentry_sdk.capture_exception(exc)
        raise exc

    def run(self, *args, task_id=None, **kwargs):
        """
        Run the job.

        This is an override of `Task.run` which is the method
        that actually gets called by Celery each time a task
        in processed. It wraps `self.do()` to handle
        logging, exceptions, termination etc.

        Most jobs need to operate within a project's working directory
        and project `File` paths are always relative to those.
        To avoid code repetition and potential errors with making paths absolute,
        this method changes into the working directory of the project.
        In the future, the project argument may be mandatory.
        """
        current_dir = os.getcwd()

        project = kwargs.get("project")
        if project:
            working_dir = get_working_dir(project)
            Path(working_dir).mkdir(parents=True, exist_ok=True)
        else:
            working_dir = current_dir

        self.begin(task_id)
        try:
            if working_dir != current_dir:
                os.chdir(working_dir)
            result = self.do(*args, **kwargs)
            return self.success(result)
        except SoftTimeLimitExceeded:
            return self.terminated()
        except Ignore as exc:
            raise exc
        except Exception as exc:
            raise self.failure(exc)
        finally:
            os.chdir(current_dir)

    def do(self, *args, **kwargs):
        """
        Do the job!

        Derived job classes should implement this method
        """
        raise NotImplementedError("Method do() is not implemented")
