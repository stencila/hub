"""
Stencila Hub Worker.

A Celery app for running jobs.
"""

import os

from celery import Celery

from jobs.archive import Archive
from jobs.clean import Clean
from jobs.convert import Convert
from jobs.decode import Decode
from jobs.encode import Encode
from jobs.pull import Pull
from jobs.session import Session
from jobs.sleep import Sleep


# Setup the Celery app
app = Celery("worker", broker=os.environ["BROKER_URL"], backend="rpc://")
app.conf.update(
    # By default Celery will keep on trying to connect to the broker forever
    # This overrides that. Initially try again immediately, then add 0.5 seconds for each
    # subsequent try (with a maximum of 3 seconds).
    # See https://github.com/celery/celery/issues/4296
    broker_transport_options={
        "max_retries": 10,
        "interval_start": 0,
        "interval_step": 0.5,
        "interval_max": 3,
    }
)

# Register the jobs
app.register_task(Archive())
app.register_task(Clean())
app.register_task(Convert())
app.register_task(Decode())
app.register_task(Encode())
app.register_task(Pull())
app.register_task(Sleep())


# It is necessary to do the following incantations
# (specifically, `bind`) to get the `task_id` (ie. `job.id`)
# attached to the task instance.
# See https://github.com/celery/celery/issues/2633 for some
# discussion on how `self.request.id` is missing without this.


@app.task(name=Session.name, base=Session, bind=True)
def session(self, *args, **kwargs):
    """Session task."""
    Session.run(self, *args, **kwargs, task_id=self.request.id)
