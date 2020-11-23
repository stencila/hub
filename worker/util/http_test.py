import pytest

from .http import HttpSession


def test_malicious_host(tempdir):
    with pytest.raises(ValueError) as excinfo:
        HttpSession().fetch_url("https://10.1.2.3/x")
    assert "10.1.2.3 is not a valid hostname" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        HttpSession().fetch_url("https://hub.stenci.la/x")
    assert "hub.stenci.la is not a valid hostname" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        HttpSession().fetch_url("https://localhost/abc")
    assert "localhost is not a valid hostname" in str(excinfo.value)
