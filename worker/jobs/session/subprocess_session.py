from config import get_node_modules_bin
from jobs.base.subprocess_job import SubprocessJob
from util.network import get_local_ip, get_random_port


class SubprocessSession(SubprocessJob):
    """
    Runs a session in a local subprocess.

    This class should only be used for trusted sessions.
    """

    def do(self, *args, **kwargs):
        """
        Start the session.

        Override of `Job.do` which updates the job state with the
        URL of the session before starting the session (which blocks
        until the job is terminated).
        """
        protocol = "ws"
        ip = get_local_ip()
        port = get_random_port()

        self.notify(state="RUNNING", url="{}://{}:{}".format(protocol, ip, port))

        return super().do(
            [
                get_node_modules_bin("executa"),
                "serve",
                "--debug",
                "--{}=0.0.0.0:{}".format(protocol, port),
            ]
        )
