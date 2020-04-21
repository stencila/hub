import subprocess

from execute.session import Session


class ProcessSession(Session):
    """
    Runs an execution session in a subprocess.

    This class is intended for development and testing only.
    """
    
    def __init__(self):
        super().__init__()
        self.process = None

    def start(self):
        self.process = subprocess.Popen(
            [
                "executa",
                "serve",
                "--debug",
                "--{}".format(self.protocol),
                "0.0.0.0:{}".format(self.port),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # TODO: use a variable, higher timeout
        try:
            self.process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.stop()

    def stop(self):
        if self.process:
            self.process.kill()
            self.process = None
