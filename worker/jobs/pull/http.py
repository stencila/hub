import ipaddress
import requests
from socket import gethostbyname
from urllib.parse import urlparse


class RemoteFileException(Exception):
    pass


def pull_http(source: dict, sink: str) -> str:
    """
    Pull a file from an HTTP source.
    """
    assert "url" in source, "HTTP source must have a URL"

    with fetch_url(source["url"]) as response:
        with open(sink, "wb") as file:
            for chunk in response:
                file.write(chunk)

    return sink


def fetch_url(url):
    url_obj = urlparse(url)

    if url_obj.hostname is None:
        raise TypeError('Url "{}" appears to have no hostname.'.format(url))

    if is_malicious_host(url_obj.hostname):
        raise RemoteFileException(
            "{} is not a valid hostname.".format(url_obj.hostname)
        )

    session = requests.Session()
    session.max_redirects = 5
    headers = {"User-Agent": "Stencila Hub HTTP Client"}
    return session.get(url, headers=headers, stream=True, allow_redirects=True)


def is_malicious_host(hostname):
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
