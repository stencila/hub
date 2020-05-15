import ipaddress
import re
import requests
from socket import gethostbyname
from urllib.parse import urlparse


class HttpSession(requests.sessions.Session):
    def __init__(self):
        super().__init__()
        self.max_redirects = 5
        self.headers = {"User-Agent": "Stencila Hub HTTP Client"}

    def get_redirect_target(self, resp):
        # Override to run each redirect target through the malicious
        # host check
        url = super().get_redirect_target(resp)
        self.check_host(url)
        return url

    def check_host(self, url):
        if url is None:
            return

        url_obj = urlparse(url)

        if url_obj.hostname is None:
            raise ValueError('Url "{}" appears to have no hostname.'.format(url))

        if self.is_malicious_host(url_obj.hostname):
            raise ValueError("{} is not a valid hostname.".format(url_obj.hostname))

    def fetch_url(self, url, stream=False):
        self.check_host(url)
        return self.get(url, stream=stream, allow_redirects=True)

    def pull(self, url, sink):
        with self.fetch_url(url, stream=True) as response:
            with open(sink, "wb") as file:
                for chunk in response:
                    file.write(chunk)

    @classmethod
    def is_malicious_host(cls, hostname):
        """Detect if user is trying to do things like connect to localhost
        or a local IP address of some kind.
        """
        if not hostname:
            return True

        if hostname.lower() in ["hub-test.stenci.la", "hub.stenci.la"]:
            return True

        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            pass
        else:
            return True  # Trying to access a site by IP

        address = gethostbyname(hostname)
        ip = ipaddress.ip_address(address)
        return ip.is_loopback or ip.is_private
