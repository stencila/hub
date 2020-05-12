from typing import Optional


class Session:
    """
    Base class for alternative types of job sessions.
    """

    protocol: str
    ip: Optional[str]
    port: Optional[int]

    def __init__(self, protocol: str = "ws"):
        self.protocol = protocol
        self.ip = None
        self.port = None

    def stop(self):
        self.ip = None
        self.port = None

    @property
    def url(self):
        return "{}://{}:{}".format(self.protocol, self.ip, self.port)
