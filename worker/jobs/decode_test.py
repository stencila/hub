import pytest

from .decode import Decode


def test_decode_to_file(tempdir):
    """Decode a Markdown file to a Stencila node."""
    job = Decode()

    tempdir.write("input.md", b"### My heading")
    result = job.run(tempdir.getpath("input.md"),)
    assert result["result"] == dict(
        type="Article", content=[dict(type="Heading", depth=3, content=["My heading"])]
    )
    assert result["log"] == []
