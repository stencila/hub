"""
Stencila Hub Overseer.

A Celery app for monitoring job and worker events.
A worker must be run with the `--events` to emit events.
See http://docs.celeryproject.org/en/stable/userguide/monitoring.html#events.
(Much of the following docstring are from there.)
"""
from datetime import datetime
import os
import warnings

from prometheus_client import start_http_server, Summary
from celery import Celery
from celery.events.receiver import EventReceiver
import httpx

app = Celery("overseer", broker=os.environ["BROKER_URL"])

# Setup API client
api = httpx.Client(
    base_url=os.path.join(os.environ["DIRECTOR_URL"], "api/"),
    headers={"content-type": "application/json", "accept": "application/json"},
    timeout=30,
)


def update_job(id, data):
    """
    Update a job.

    Sends a PATCH request to the `director` to update the
    state of the job.
    """
    response = api.patch("jobs/{}".format(id), json=data)
    if response.status_code != 200:
        warnings.warn(response.text)


def worker_event(data):
    """
    Create a worker event.

    Sends a POST request to the `director` with a new
    worker event. Because of the intricacies of uniquely
    identifying workers, we send events, rather trying to
    resolve ids here.
    """
    response = api.post("workers/events", json=data)
    if response.status_code != 200:
        warnings.warn(response.text)


# Handlers for task events


def task_sent(event):
    """Sent when a task message is published and the task_send_sent_event setting is enabled."""
    print("task_sent", event)


def task_received(event):
    """Sent when the worker receives a task."""
    update_job(
        event["uuid"],
        {
            "status": event.get("state", "RECEIVED"),
            "retries": event.get("retries"),
            "worker": event.get("hostname"),
        },
    )


def task_started(event):
    """Sent just before the worker executes the task."""
    update_job(
        event["uuid"],
        {
            "status": event.get("state", "STARTED"),
            "began": datetime.fromtimestamp(event.get("timestamp")).isoformat(),
            "worker": event.get("hostname"),
        },
    )


def task_succeeded(event):
    """
    Sent if the task executed successfully.

    Run-time is the time it took to execute the task using the pool.
    (Starting from the task is sent to the worker pool, and ending when the pool
    result handler callback is called).
    """
    update_job(
        event["uuid"],
        {
            "status": event.get("state", "SUCCESS"),
            "ended": datetime.fromtimestamp(event.get("timestamp")).isoformat(),
            "result": event.get("result"),
            "runtime": event.get("runtime"),
            "worker": event.get("hostname"),
        },
    )


def task_failed(event):
    """Sent if the execution of the task failed."""
    update_job(
        event["uuid"],
        {
            "status": event.get("state", "FAILED"),
            "ended": datetime.fromtimestamp(event.get("timestamp")).isoformat(),
            "log": [
                {
                    "level": 0,
                    "message": event.get("exception"),
                    "stack": event.get("traceback"),
                }
            ],
            "worker": event.get("hostname"),
        },
    )


def task_rejected(event):
    """Sent if the task was rejected by the worker, possibly to be re-queued or moved to a dead letter queue."""
    print("task_rejected", event)


def task_revoked(event):
    """
    Sent if the task has been revoked (Note that this is likely to be sent by more than one worker).

    terminated is set to true if the task process was terminated,
    and the signum field set to the signal used.
    expired is set to true if the task expired.
    """
    update_job(
        event["uuid"],
        {
            "status": "TERMINATED" if event.get("terminated") else "REVOKED",
            "ended": datetime.fromtimestamp(event.get("timestamp")).isoformat(),
            "worker": event.get("hostname"),
        },
    )


def task_retried(event):
    """Sent if the task failed, but will be retried in the future."""
    print("task_retried", event)


# Handlers for worker events


def worker_handler(event):
    """
    Handle one of the three worker events.

    - online: A worker has connected to the broker and is online.
    - heartbeat: Sent by a worker every `event.freq` seconds.
    - offline: A worker has disconnected from the broker.

    Contrary to the Celery docs, at the time of writing, these three
    event types have the same fields so we have a single handler and
    do most of the logic handling in Django.
    """
    worker_event(event)


# Monitoring metrics

event_processing = Summary(
    "event_processing_seconds", "Summary of event processing duration"
)


class Receiver(EventReceiver):
    """Extends Celery's `EventReceiver` class to implement monitoring intrumentation."""

    def __init__(self, connection):
        """Override that connects above handlers to event types."""
        super().__init__(
            connection,
            handlers={
                "task-sent": task_sent,
                "task-received": task_received,
                "task-started": task_started,
                "task-succeeded": task_succeeded,
                "task-failed": task_failed,
                "task-rejected": task_rejected,
                "task-revoked": task_revoked,
                "task-retried": task_retried,
                "worker-online": worker_handler,
                "worker-heartbeat": worker_handler,
                "worker-offline": worker_handler,
            },
        )

    def process(self, type: str, event):
        """Override that increments the event counter."""
        with event_processing.time():
            return super().process(self, type, event)


# Start the HTTP server to expose metrics
start_http_server(4040)

# Connect handlers to events
with app.connection() as connection:
    receiver = Receiver(connection)
    receiver.capture(limit=None, timeout=None, wakeup=True)
