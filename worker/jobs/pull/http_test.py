import pytest

from .http import pull_http
from .base import RemoteFileException


def test_malicious_host():
    with pytest.raises(RemoteFileException) as excinfo:
        pull_http({"url": "https://10.1.2.3/x"}, "test.xml")
    assert "10.1.2.3 is not a valid hostname" in str(excinfo.value)
    with pytest.raises(RemoteFileException) as excinfo:
        pull_http({"url": "https://hub.stenci.la/x"}, "test.xml")
    assert "hub.stenci.la is not a valid hostname" in str(excinfo.value)
    with pytest.raises(RemoteFileException) as excinfo:
        pull_http({"url": "https://localhost/abc"}, "test.xml")
    assert "localhost is not a valid hostname" in str(excinfo.value)
