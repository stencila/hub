import os

from config import get_node_modules_bin, get_snapshot_dir
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

        # Project to start session for
        project = kwargs.get("project")
        assert project is not None, "A project id is required to start a session"

        # If a snapshot directory is specified then change into it
        # (if not a snapshot session then we will already be in the project's working directory)
        snapshot = kwargs.get("snapshot")
        if snapshot:
            os.chdir(get_snapshot_dir(project, snapshot))

        ip = get_local_ip()
        ports = {"ws": get_random_port(), "http": get_random_port()}

        urls = dict(
            (protocol, f"{protocol}://{ip}:{port}") for protocol, port in ports.items()
        )
        self.notify(state="RUNNING", urls=urls)

        return super().do(
            [get_node_modules_bin("executa"), "serve", "--debug"]
            + [f"--{protocol}=0.0.0.0:{port}" for protocol, port in ports.items()]
        )
