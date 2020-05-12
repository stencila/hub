"""
Module that defines the `SubprocessSession` class.
"""

import subprocess

from .network import get_local_ip, get_random_port
from .session import Session


class SubprocessSession(Session):
    """
    Runs a session in a local subprocess.

    This class should only be used for trusted sessions.
    """

    def __init__(self):
        super().__init__()
        self.ip = get_local_ip()
        self.port = get_random_port()
        self.process = subprocess.Popen(
            [
                "node",
                "/usr/lib/node_modules/@stencila/executa/dist/cli/cli/index.js",
                "serve",
                "--debug",
                "--{}=0.0.0.0:{}".format(self.protocol, self.port),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def start(self):
        """Start the session."""
        # TODO: use a variable, higher timeout
        try:
            self.process.wait(timeout=60 * 60)
        except subprocess.TimeoutExpired:
            self.stop()

    def stop(self):
        """Stop the session."""
        if self.process:
            self.process.kill()
            self.process = None
