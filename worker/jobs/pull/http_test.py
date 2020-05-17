import pytest

from .http import pull_http


def test_malicious_host(tempdir):
    with pytest.raises(ValueError) as excinfo:
        pull_http({"url": "https://10.1.2.3/x"}, tempdir.path, "test.xml")
    assert "10.1.2.3 is not a valid hostname" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        pull_http({"url": "https://hub.stenci.la/x"}, tempdir.path, "test.xml")
    assert "hub.stenci.la is not a valid hostname" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        pull_http({"url": "https://localhost/abc"}, tempdir.path, "test.xml")
    assert "localhost is not a valid hostname" in str(excinfo.value)
