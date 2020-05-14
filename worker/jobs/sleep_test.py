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

    def update_state(state, meta):
        assert state == "RUNNING"
        index = current["index"]
        assert meta["log"][index]["level"] == INFO
        assert meta["log"][index]["message"].startswith("This is repetition {}".format(index + 1))
        current["index"] += 1

    job.update_state = update_state

    job.run()
