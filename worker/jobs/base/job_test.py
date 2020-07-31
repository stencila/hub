from unittest import mock

import pytest
from celery.exceptions import Ignore

from .job import Job, DEBUG, INFO, WARN, ERROR


def test_logging():
    """On each log entry update_state is called with the log."""
    job = Job()
    job.begin(task_id=4321)

    current = {}

    def send_event(self, event, **kwargs):
        assert event == "task-logged"
        current["state"] = kwargs.get("state")
        current["log"] = kwargs.get("log")

    with mock.patch(
        "celery.Task.send_event", new=send_event,
    ):

        for index, level in enumerate(["error", "warn", "info", "debug"]):
            getattr(job, level)("{} message".format(level))

            log = job.log_entries[-1]
            assert "time" in log
            assert log["level"] == index
            assert log["message"] == "{} message".format(level)
            assert current["state"] == "RUNNING"
            assert current["log"] == job.log_entries


def test_success():
    """Returns both result and log."""
    job = Job()
    job.begin()
    returns = job.success(42)
    assert returns["result"] == 42
    assert returns["log"] == []

def test_terminated():
    """Calls flush"""
    job = Job()
    job.begin()
    job.terminated()


def test_do_unimplemented():
    """Derived classes must implement do()."""
    job = Job()
    with pytest.raises(NotImplementedError) as excinfo:
        job.run()
    assert "Method do() is not implemented" in str(excinfo.value)
