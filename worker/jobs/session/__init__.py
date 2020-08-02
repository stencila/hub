import os
from typing import Optional, List

from jobs.base.job import Job

# If on a K8s cluster then use the K8s-based sessions
# otherwise use the subsprocess-based session
if "KUBERNETES_SERVICE_HOST" in os.environ:
    from .kubernetes_session import KubernetesSession

    Session = KubernetesSession
else:
    from .subprocess_session import SubprocessSession

    Session = SubprocessSession

Session.name = "session"
