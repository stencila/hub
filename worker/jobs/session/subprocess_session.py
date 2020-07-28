"""
Module that defines the `SubprocessSession` class.
"""

from jobs.base.subprocess_job import SubprocessJob

from .network import get_local_ip, get_random_port
from .session import Session


class SubprocessSession(Session, SubprocessJob):
    """
    Runs a session in a local subprocess.

    This class should only be used for trusted sessions.
    """

    def __init__(self):
        super().__init__()
        self.ip = get_local_ip()
        self.port = get_random_port()

    def do(self, *args, **kwargs):
        """
        Start the session.

        Override of `Job.do` which updates the job state with the
        URL of the session before running the session (which blocks
        until the job is terminated).
        """
        self.update_state(state="RUNNING", meta=dict(url=self.url))
        return super().do(
            [
                "node",
                "/usr/lib/node_modules/@stencila/executa/dist/cli/cli/index.js",
                "serve",
                "--debug",
                "--{}=0.0.0.0:{}".format(self.protocol, self.port),
            ]
        )
