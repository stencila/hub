import sys
from unittest import mock

import pytest
from celery.exceptions import Ignore

from .subprocess_job import SubprocessJob
from .job import Job, DEBUG, INFO, WARN, ERROR


def test_success():
    """The stdout from the subprocess is the job result."""
    job = SubprocessJob()
    result = job.run(["echo", "Beep, boop"])
    assert result["result"] == "Beep, boop\n"
    assert result["log"] == []


@pytest.mark.skipif(sys.platform != "linux", reason="flakey on other platforms")
def test_input():
    """The input arg is sent to stdin."""
    job = SubprocessJob()
    result = job.run(["sed", "-e", ""], input=b"Yo!")
    assert result["result"] == "Yo!"
    assert result["log"] == []


@pytest.mark.skipif(sys.platform != "linux", reason="flakey on other platforms")
def test_failure():
    """If the subprocess returns a non zero exit code then the job fails."""
    job = SubprocessJob()

    def update_state(state, meta):
        assert state == "RUNNING"

    job.update_state = update_state

    with pytest.raises(RuntimeError) as excinfo:
        job.run(["sleep", "foo"])
    assert "Subprocess exited with non-zero code" in str(excinfo.value)


def test_logging_json():
    """If a line on stderr looks like a JSON log entry then it is treated as one."""
    job = SubprocessJob()

    def update_state(state, meta):
        assert state == "RUNNING"
        entry = meta["log"][-1]
        assert entry["level"] == WARN
        assert entry["message"] == "A warning message"

    job.update_state = update_state

    job.run(
        ["bash", "-c", """echo '{"level": 1, "message": "A warning message"}' 1>&2"""]
    )


def test_logging_ongoing():
    """While the job is running we should get ongoing updates to the log."""
    job = SubprocessJob()

    current = {"index": 0}

    def update_state(state, meta):
        assert state == "RUNNING"
        index = current["index"]
        assert meta["log"][index]["level"] == INFO
        assert meta["log"][index]["message"] == "{}\n".format(index)
        current["index"] += 1

    job.update_state = update_state

    job.run(
        [
            "bash",
            "-c",
            # A loop that echos to stderr
            "for index in 0 1 2 3 4 5; do sleep 0.1; echo $index 1>&2 ; done",
        ]
    )
