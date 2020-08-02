import pytest
from celery.exceptions import SoftTimeLimitExceeded

from .kubernetes_session import KubernetesSession


@pytest.mark.skipif(
    KubernetesSession.api_instance is None, reason="can only run if K8s is available"
)
def test_k8s_session():
    """
    Test starting and stopping session.

    Once the session is running, raises a `SoftTimeLimitExceeded`
    exception to stop the session.
    """
    session = KubernetesSession()

    context = {"step": 0}

    def send_event(event, task_id, state, **kwargs):
        context["step"] += 1
        if context["step"] == 1:
            assert state == "LAUNCHING"
        elif context["step"] == 2:
            assert state == "RUNNING"
            raise SoftTimeLimitExceeded

    session.send_event = send_event

    assert session.name is None
    session.run()
    assert session.name is None
