from util.network import get_local_ip, get_random_port


class Session:
    """
    Base class for alternative types of job sessions.
    """

    protocol: str
    ip: str = get_local_ip()
    port: int

    def __init__(self, protocol: str = "ws"):
        self.protocol = protocol
        self.ip = Session.ip
        self.port = get_random_port()

    @property
    def url(self):
        return "{}://{}:{}".format(self.protocol, self.ip, self.port)
