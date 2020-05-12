import pytest

from .kubernetes_session import KubernetesSession


@pytest.mark.skipif(
    KubernetesSession.api_instance is None, reason="can only run if K8s is available"
)
def test_k8s_session():
    session = KubernetesSession()
    assert session.name is not None
    assert session.ip is not None
    assert session.port is not None

    session.start()

    session.stop()
    assert session.name is None
    assert session.ip is None
    assert session.port is None
