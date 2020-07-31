from typing import Optional, List

from jobs.base.job import Job

from .subprocess_session import SubprocessSession
from .kubernetes_session import KubernetesSession


class Session(SubprocessSession):

    name = "session"
