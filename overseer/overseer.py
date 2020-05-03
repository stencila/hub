"""
Stencila Hub Overseer.

A Celery app for monitoring job and worker events.
A worker must be run with the `--events` to emit events.
See http://docs.celeryproject.org/en/stable/userguide/monitoring.html#events.
"""
from datetime import datetime
import os
import warnings

from celery import Celery
import httpx

celery = Celery("overseer", broker=os.environ["BROKER_URL"])

# Setup API client
api = httpx.Client(
    base_url=os.path.join(os.environ["DIRECTOR_URL"], "api/"),
    headers={"content-type": "application/json", "accept": "application/json",},
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
    print("task_sent", event)


def task_received(event):
    update_job(
        event["uuid"],
        {
            "status": event.get("state", "RECEIVED"),
            "retries": event.get("retries"),
            "worker": event.get("hostname"),
        },
    )


def task_started(event):
    update_job(
        event["uuid"],
        {
            "status": event.get("state", "STARTED"),
            "began": datetime.fromtimestamp(event.get("timestamp")).isoformat(),
            "worker": event.get("hostname"),
        },
    )


def task_succeeded(event):
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
    print("task_rejected", event)


def task_revoked(event):
    update_job(
        event["uuid"],
        {
            "status": "TERMINATED" if event.get("terminated") else "REVOKED",
            "ended": datetime.fromtimestamp(event.get("timestamp")).isoformat(),
            "worker": event.get("hostname"),
        },
    )


def task_retried(event):
    print("task_retried", event)


# Handlers for worker events


def worker_handler(event):
    """
    Handler for all three worker events: online, offline, heartbeat.

    Contrary to the Celery docs, at the time of writing, these three
    event types have the same fields so we have a single handler and
    do most of the logic handling in Django.
    """
    worker_event(event)


# Connect handler to events

with celery.connection() as connection:
    receiver = celery.events.Receiver(
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
    receiver.capture(limit=None, timeout=None, wakeup=True)
