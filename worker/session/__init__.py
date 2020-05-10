from .subprocess_session import SubprocessSession
from .kubernetes_session import KubernetesSession


def create():
    """
    Create a new session.

    The class of session is determined by the environment,
    including environment variables.
    """
    #return KubernetesSession()
    return SubprocessSession()
