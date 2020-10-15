from typing import Type, Union

from .kubernetes_session import KubernetesSession, api_instance
from .subprocess_session import SubprocessSession

# If on a K8s is available then use that
# otherwise use the subsprocess-based session
Session: Type[Union[KubernetesSession, SubprocessSession]]
if api_instance is not None:
    Session = KubernetesSession
else:
    Session = SubprocessSession

Session.name = "session"
