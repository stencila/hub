from typing import Dict, Any
from pathlib import Path
import tempfile
import ipaddress
import mimetypes
import os
import re
import requests
import shutil
from socket import gethostbyname
from urllib.parse import urlparse

Files = Dict[str, Dict[str, Any]]


def begin_pull(working_dir: str) -> str:
    """
    Begin a pull job.

    Creates a temporary directory, within the working directory,
    for the pull to create files. Returns absolute path to
    the temporary directory.
    """
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    return tempfile.mkdtemp(dir=working_dir)


def end_pull(working_dir: str, path: str, temporary_dir: str) -> Files:
    """
    End a pull job.

    Collects file information for temporary directory,
    removes the existing contents of path, and replaces it with
    the contents of temporary. Returns dictionary of file information.

    working: The working directory to pull the source into
    path: The path inside the working directory to pull the source to
    temporary: The temporary directory used for the pull
    """
    files = {}
    for (dirpath, dirnames, filenames) in os.walk(temporary_dir):
        for filename in filenames:
            absolute_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(absolute_path, temporary_dir)
            mimetype, encoding = mimetypes.guess_type(relative_path)
            files[relative_path] = {
                "size": os.path.getsize(absolute_path),
                "mimetype": mimetype,
                "encoding": encoding,
                "modified": os.path.getmtime(absolute_path),
            }

    # TODO: Remove existing files at the path from a previous pull
    # Not done at present pending what those paths might be e.g. `.`, `file.txt`, `dir`

    # Move from temporary to working (with overwrite)
    for subpath in os.listdir(temporary_dir):
        shutil.move(
            os.path.join(temporary_dir, subpath), os.path.join(working_dir, subpath)
        )

    # Remove temporary directory
    shutil.rmtree(temporary_dir, ignore_errors=True)

    return files


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
