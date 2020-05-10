from session.kubernetes_session import KubernetesSession


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
