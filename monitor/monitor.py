"""
Stencila Hub Monitor.

A Celery app for monitoring worker events.
A worker must be run with the `--events` to emit events.
See http://docs.celeryproject.org/en/stable/userguide/monitoring.html#events.
"""
from datetime import datetime
import os

from celery import Celery
import httpx

celery = Celery("monitor", broker=os.environ["BROKER_URL"])

# Setup API client
api = httpx.Client(
    base_url=os.path.join(os.environ["DIRECTOR_URL"], "api/jobs/"),
    headers={"content-type": "application/json", "accept": "application/json",},
    auth=tuple(os.environ["DIRECTOR_AUTH"].split(":")),
)


def update_job(id, data):
    """
    Update the job.

    Sends a PATCH request to the director to update the
    state of the job.
    """
    response = api.patch(id, json=data)
    if response.status_code != 200:
        # Generate a warning if not successful
        print(response.json())


# The following are all the available task events


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
            "log": [{
                "level": 0,
                "message": event.get("exception"),
                "stack": event.get("traceback")
            }],
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


def worker_online(event):
    print("worker_online", event)


def worker_heartbeat(event):
    pass #print("worker_heartbeat", event)


def worker_offline(event):
    print("worker_offline", event)


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
            "worker-online": worker_online,
            "worker-heartbeat": worker_heartbeat,
            "worker-offline": worker_offline,
        },
    )
    receiver.capture(limit=None, timeout=None, wakeup=True)
