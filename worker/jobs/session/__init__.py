from typing import Optional, List

from jobs.base.job import Job

from .subprocess_session import SubprocessSession
from .kubernetes_session import KubernetesSession

# Session = KubernetesSession
Session = SubprocessSession
Session.name = "session"
