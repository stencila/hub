from contextlib import ContextDecorator
from unittest import mock

import httpx
import pytest

from util.working_directory import working_directory

from .http import pull_http


class MockedHttpxStreamResponse(ContextDecorator):
    """
    VCR does not like recording HTTPX stream requests so mock it.
    """

    def __init__(self, method, url, **kwargs):
        self.response = httpx.get(url)

    def __getattr__(self, attr):
        return getattr(self.response, attr)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return self


@pytest.mark.vcr
@mock.patch("httpx.stream", MockedHttpxStreamResponse)
def test_extension_from_mimetype(tempdir):
    with working_directory(tempdir.path):
        files = pull_http({"url": "https://httpbin.org/get"})
        assert files["get.json"]["mimetype"] == "application/json"

        files = pull_http({"url": "https://httpbin.org/image/png"}, path="image")
        assert files["image.png"]["mimetype"] == "image/png"

        files = pull_http({"url": "https://httpbin.org/html"}, path="content")
        assert files["content.html"]["mimetype"] == "text/html"

        files = pull_http({"url": "https://httpbin.org/html"}, path="foo.bar")
        assert files["foo.bar"]["mimetype"] is None


# For some reason the status code does not work with VCR record
def test_status_codes(tempdir):
    with pytest.raises(RuntimeError) as excinfo:
        pull_http({"url": "https://httpbin.org/status/404"})
    assert "Error when fetching https://httpbin.org/status/404: 404" in str(
        excinfo.value
    )
