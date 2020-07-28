import sys

import pytest

from .decode import Decode


@pytest.mark.skip(reason="Failing test for currently non-essential job")
@pytest.mark.skipif(sys.platform != "linux", reason="flakey on other platforms")
def test_decode_from_file(tempdir):
    """Decode a Markdown file to a Stencila node."""
    job = Decode()
    tempdir.write("input.md", b"### My heading")
    result = job.run(tempdir.getpath("input.md"),)
    assert result["result"] == dict(
        type="Article", content=[dict(type="Heading", depth=3, content=["My heading"])]
    )
    assert result["log"] == []
