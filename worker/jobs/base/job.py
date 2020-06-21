from datetime import datetime
from typing import Any, Optional
import traceback

import celery
from celery import states
from celery.exceptions import Ignore, SoftTimeLimitExceeded

# Log levels
# These are the same as used in https://github.com/stencila/logga
ERROR = 0
WARN = 1
INFO = 2
DEBUG = 3


class Job(celery.Task):
    """
    Base class for all Jobs.

    Extends Celery's Task class to handle logging and
    termination of jobs.
    """

    def __init__(self):
        super().__init__()
        self.log_entries = None

    def begin(self):
        """
        Begin the job.

        Because the `run()` method is executed several times
        for each task instance, this method performs any
        initialization in advance.
        """
        self.log_entries = []

    def log(self, level: int, message: str, **kwargs):
        """
        Create a log entry.

        This appends an entry to the log and updates the
        state with the log as metadata. This makes the
        log and any extra details available to the `manager`.
        (see the `update_job` for how these are extracted)
        """
        self.log_entries.append(
            dict(time=datetime.utcnow().isoformat(), level=level, message=message)
        )
        self.update_state(state="RUNNING", meta=dict(log=self.log_entries, **kwargs))

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

        This method updates the job state to the custom state
        `TERMINATED` and raises `Ignore` so that state is not overwritten
        by Celery. See https://www.distributedpython.com/2018/09/28/celery-task-states/.
        """
        self.update_state(state="TERMINATED", meta=dict(log=self.log_entries))
        raise Ignore()

    def failure(self, exc: Exception):
        """
        Job has failed due to an exception.

        TODO: Report to Sentry.
        """
        raise exc

    def run(self, *args, **kwargs):
        """
        Run the job.

        This is an override of `Task.run` which is the method
        that actually gets called by Celery each time a task
        in processed. It is wraps `self.do()` to handle
        logging, exceptions, termination etc.
        """
        self.begin()
        try:
            result = self.do(*args, **kwargs)
            return self.success(result)
        except SoftTimeLimitExceeded:
            return self.terminated()
        except Exception as exc:
            raise self.failure(exc)

    def do(self, *args, **kwargs):
        """
        Do the job!

        Derived job classes should implement this method
        """
        raise NotImplementedError("Method do() is not implemented")
