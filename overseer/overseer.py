"""
Stencila Hub Overseer.

A Celery app for monitoring jobs and workers. It has three main
functions:

- in the main thread, it captures the job and worker events emitted
  by Celery and translates them into data that is posted to the `manager`'s API.
  See http://docs.celeryproject.org/en/stable/userguide/monitoring.html#events.

- in another thread, it periodically queries the Celery API to collect information on
  the length of queues and the number of workers listening to each queue

- it serves Prometheus metrics that are scraped by `monitor` (which can in turn
  be used by Kubernetes for scaling) workers

Workers must be run with the `--events` option to emit events
for the `overseer` to handle.

Note: This ignores the `result` of `task_succeeded` events and
the `exception` and `traceback` arguments of `task_failed` events.
This is partly to avoid duplicating logic for handling those (see `update_job`
function in `manager`) and because the events are not intended
for this purpose (the results should be used for that, which is what
`update_job` does; see https://github.com/celery/celery/issues/2190#issuecomment-51609500).
"""
from datetime import datetime
from typing import Dict, List, Set, Union
import json
import logging
import os
import threading
import time

from prometheus_client import start_http_server, Summary, Gauge
from celery import Celery
from celery.events.receiver import EventReceiver
from celery.utils.objects import FallbackContext
import amqp.exceptions
import httpx

DEBUG = os.environ.get("DEBUG")
logging.basicConfig(level="DEBUG" if DEBUG is not None else "INFO")

logger = logging.getLogger(__name__)


app = Celery("overseer", broker=os.environ["BROKER_URL"])

# Monitoring metrics (these are updated by `Receiver` and `Collector` below)

event_processing = Summary(
    "overseer_event_processing", "Summary of event processing duration"
)

queue_length = Gauge("overseer_queue_length", "Number of jobs in the queue.", ["queue"])

workers_count = Gauge(
    "overseer_workers_count", "Number of workers listening to the queue.", ["queue"]
)

queue_length_worker_ratio = Gauge(
    "overseer_queue_length_worker_ratio",
    "Ratio of the number of jobs to the number of workers for each queue.",
    ["queue"],
)

# Manager API

client = httpx.Client(
    base_url=os.path.join(os.environ["MANAGER_URL"], "api/"),
    headers={"content-type": "application/json", "accept": "application/json"},
    timeout=30,
)


def request(method: str, url: str, **kwargs):
    """Send a request to the `manager`."""
    try:
        request = client.build_request(method=method, url=url, **kwargs)
        response = client.send(request)
        if response.status_code != 200:
            logger.error(response.text)
    except Exception as exc:
        logger.error(str(exc))


Event = Dict[str, Union[str, int, float]]


def get_event_time(event: Event):
    """Get the event timestamp and convert it into ISO format as expected by the Hub."""
    return datetime.fromtimestamp(float(event.get("timestamp", 0))).isoformat() + "Z"


# Handlers for task events


def update_job(id, data: dict):
    """
    Update a job.

    Sends a PATCH request to the `manager` to update the
    state of the job. Reused below for individual task event handlers.
    """
    request("PATCH", "jobs/{}".format(id), json=data)


def task_sent(event: Event):
    """Sent when a task message is published and the task_send_sent_event setting is enabled."""
    print("task_sent", event)


def task_received(event: Event):
    """Sent when the worker receives a task."""
    update_job(
        event["uuid"],
        {
            "status": event.get("state", "RECEIVED"),
            "retries": event.get("retries"),
            "worker": event.get("hostname"),
        },
    )


def task_started(event: Event):
    """Sent just before the worker executes the task."""
    update_job(
        event["uuid"],
        {
            "status": event.get("state", "STARTED"),
            "began": get_event_time(event),
            "worker": event.get("hostname"),
        },
    )


def task_succeeded(event: Event):
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
            "ended": get_event_time(event),
            "runtime": event.get("runtime"),
            "worker": event.get("hostname"),
        },
    )


def task_updated(event: Event):
    """
    Sent when the task updates its state or send other data.

    This is a custom event, see `worker.Job` for when
    it is emitted.
    """
    data = {"status": event.get("state", "RUNNING")}

    # Rather than send all data, only pass on known fields
    for field in ["log", "url"]:
        value = event.get(field)
        if value:
            data.update({field: value})

    update_job(event["task_id"], data)


def task_failed(event: Event):
    """Sent if the execution of the task failed."""
    update_job(
        event["uuid"],
        {
            "status": event.get("state", "FAILURE"),
            "ended": get_event_time(event),
            "worker": event.get("hostname"),
        },
    )


def task_rejected(event: Event):
    """Sent if the task was rejected by the worker, possibly to be re-queued or moved to a dead letter queue."""
    print("task_rejected", event)


def task_revoked(event: Event):
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
            "ended": get_event_time(event),
            "worker": event.get("hostname"),
        },
    )


def task_retried(event: Event):
    """Sent if the task failed, but will be retried in the future."""
    print("task_retried", event)


# Keep track of the queues that each worker is listening to
# so that we can update queue_length_worker_ratio
WORKERS: Dict[str, List[str]] = {}

# Keep track of all queues ever seen by this process
# so that we can set metrics to zero if necessary
QUEUES: Set[str] = set()


def add_worker(hostname: str):
    """
    Add a worker.

    Gets additional stats and the queues for the worker.
    The list of queues may initially be empty so try multiple
    times.
    """
    logger.info("Adding worker: {}.".format(hostname))

    inspect = app.control.inspect([hostname])
    queues = None
    stats = None
    trials = 0
    while queues is None and stats is None and trials < 1000:
        queues = inspect.active_queues()
        queues = queues.get(hostname) if queues else None
        stats = inspect.stats()
        stats = stats.get(hostname) if stats else None
        trials += 1
        time.sleep(0.1)

    if queues is None or stats is None:
        logger.error(
            "Unable to fetch queues and/or stats for worker: {}".format(hostname)
        )

    global QUEUES
    if queues is not None:
        queues = [queue["name"] for queue in queues]
        WORKERS[hostname] = queues
        QUEUES = QUEUES.union(queues)

    return (queues, stats)


def remove_worker(hostname: str):
    """Remove a worker."""
    logger.info("Removing worker: {}.".format(hostname))

    if hostname in WORKERS:
        del WORKERS[hostname]


# Handlers for worker events


def worker_online(event: Event):
    """
    Sent when a worker has connected to the broker.

    Fetches more information on the worker and creates a new worker
    object on the `manager`.
    """
    hostname = str(event.get("hostname"))
    queues, stats = add_worker(hostname)

    request(
        "POST",
        "workers/online",
        json=dict(details=dict(queues=queues, stats=stats), **event),
    )


def worker_heartbeat(event: Event):
    """
    Sent by a worker every `event.freq` seconds.

    Sends a POST request to the `manager` to create a heartbeat.
    Because of the intricacies of uniquely identifying workers,
    rather trying to resolve which worker this heartbeat is for here,
    we sent the entire event to the `manager` and do it over there.
    """
    hostname = str(event.get("hostname"))
    if hostname not in WORKERS:
        add_worker(hostname)

    request("POST", "workers/heartbeat", json=event)


def worker_offline(event: Event):
    """
    Sent when a worker has disconnected from the broker.

    Sends a POST request to the `manager` to mark the
    worker as finished.
    """
    hostname = str(event.get("hostname"))
    if hostname in WORKERS:
        remove_worker(hostname)

    request("POST", "workers/offline", json=event)


class Receiver(EventReceiver):
    """
    A class for receiving events about jobs and workers.

    Extends Celery's `EventReceiver` class to implement monitoring intrumentation.
    """

    def __init__(self, connection):
        """Override that connects above handlers to event types."""
        super().__init__(
            connection,
            handlers={
                "task-sent": task_sent,
                "task-received": task_received,
                "task-started": task_started,
                "task-updated": task_updated,
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

    def process(self, type: str, event: Event):
        """Override that increments the event counter."""
        logger.debug("Event received: {0}: {1}".format(type, json.dumps(event)[:1000]))
        with event_processing.time():
            return super().process(type, event)


class Collector(threading.Thread):
    """
    A thread for collecting information on queues and workers.

    Based on, the now archived, https://github.com/zerok/celery-prometheus-exporter.
    """

    periodicity_seconds = 15
    workers_ping_timeout_seconds = 10

    def __init__(self, app: Celery):
        """Create the collector thread."""
        self.app = app
        self.connection = app.connection_or_acquire()
        if isinstance(self.connection, FallbackContext):
            self.connection = self.connection.fallback()
        super().__init__()

    def run(self):
        """Run the collector thread."""
        while True:
            # `ping` workers; returns a list of workers e.g. `[{'worker@host': {'ok': 'pong'}}, ...]`
            try:
                workers = self.app.control.ping(
                    timeout=self.workers_ping_timeout_seconds
                )
                logger.debug("Workers pinged: {}.".format(len(workers)))
            except Exception as exc:
                workers = []
                logger.error("Error pinging workers: {}".format(str(exc)))

            # Update `WORKERS` with list of workers that have been
            # successfully pinged.
            hostnames = [list(worker.keys())[0] for worker in workers]
            for hostname in hostnames:
                if hostname not in WORKERS:
                    add_worker(hostname)
            for hostname in list(WORKERS.keys()):
                if hostname not in hostnames:
                    remove_worker(hostname)

            # Update metrics for each queue
            for queue in QUEUES:
                try:
                    length = self.connection.default_channel.queue_declare(
                        queue=queue, passive=True
                    ).message_count
                except (amqp.exceptions.ChannelError,) as exc:
                    logger.warning(
                        "Queue Not Found: {}. Setting its value to zero. Error: {}".format(
                            queue, str(exc)
                        )
                    )
                    length = 0

                workers = len(
                    set(
                        [
                            hostname
                            for hostname, queues in WORKERS.items()
                            if queue in queues
                        ]
                    )
                )

                queue_length.labels(queue).set(length)
                workers_count.labels(queue).set(workers)
                queue_length_worker_ratio.labels(queue).set(length / max(0.5, workers))

            time.sleep(self.periodicity_seconds)


# Start the HTTP server to expose metrics
start_http_server(4040)

# Start the collector
collector = Collector(app=app)
collector.daemon = True
collector.start()

# Start the receiver
with app.connection() as connection:
    receiver = Receiver(connection)
    receiver.capture(limit=None, timeout=None, wakeup=True)
