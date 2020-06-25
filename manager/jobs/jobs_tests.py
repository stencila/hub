import pytest

from accounts.models import Account
from jobs.jobs import dispatch_job
from jobs.models import Job, JobStatus


@pytest.mark.skip(reason="in flux")
@pytest.mark.django_db
def test_dispatch_parallel():
    Account.objects.create(name="stencila")

    parent = Job.objects.create(method="parallel")
    parent.children.set(
        [
            Job.objects.create(method="sleep"),
            Job.objects.create(method="sleep"),
            Job.objects.create(method="sleep"),
        ]
    )

    dispatch_job(parent)

    assert parent.status is None
    for child in parent.children.all():
        assert child.status == JobStatus.DISPATCHED.value


@pytest.mark.skip(reason="in flux")
@pytest.mark.django_db
def test_dispatch_series():
    Account.objects.create(name="stencila")

    parent = Job.objects.create(method="series")
    parent.children.set(
        [
            Job.objects.create(method="sleep"),
            Job.objects.create(method="sleep"),
            Job.objects.create(method="sleep"),
        ]
    )

    dispatch_job(parent)

    assert parent.status is None
    children = parent.children.all()
    assert children[0].status == JobStatus.DISPATCHED.value
    assert children[1].status is None
    assert children[2].status is None
