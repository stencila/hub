import pytest

from .base.job import INFO
from .sleep import Sleep


def test_sleep():
    """
    A simple test of the sleep job.

    Given that this job class is mainly just for integration
    testing, don't try to do anything fancy here.
    """
    job = Sleep()

    current = {"index": 0}

    def send_event(event, **kwargs):
        assert kwargs.get("state") == "RUNNING"
        index = current["index"]
        assert kwargs["log"][index]["level"] == INFO
        assert kwargs["log"][index]["message"].startswith(
            "This is repetition {}".format(index + 1)
        )
        current["index"] += 1

    job.send_event = send_event

    job.run()
