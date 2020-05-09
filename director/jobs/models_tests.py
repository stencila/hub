import pytest

from accounts.models import Account
from jobs.models import Queue, Zone


@pytest.mark.django_db
def test_queue_get_or_create():
    acme = Account.objects.create(name="acme")

    # Existing zone
    north = Zone.objects.create(account=acme, name="north")
    queue, created = Queue.get_or_create(queue_name="north", account_name="acme")
    assert queue.zone == north
    assert queue.priority == 0
    assert queue.untrusted is False
    assert queue.interrupt is False

    # Implicitly created zone
    queue, created = Queue.get_or_create(queue_name="south:2", account_name="acme")
    south = Zone.objects.get(account=acme, name="south")
    assert queue.zone == south
    assert queue.priority == 2
    assert queue.untrusted is False
    assert queue.interrupt is False

    # Queue that accepts untrusted jobs
    queue, created = Queue.get_or_create(
        queue_name="north:2:untrusted", account_name="acme"
    )
    assert queue.zone == north
    assert queue.priority == 2
    assert queue.untrusted is True
    assert queue.interrupt is False

    # Queue that accepts untrusted and interruptable jobs
    queue, created = Queue.get_or_create(
        queue_name="north:2:untrusted:interrupt", account_name="acme"
    )
    assert queue.zone == north
    assert queue.priority == 2
    assert queue.untrusted is True
    assert queue.interrupt is True
