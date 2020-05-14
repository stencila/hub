import pytest

from .encode import Encode


def test_encode_to_file(tempdir):
    """Encode a Stencila node to a Markdown file"""
    job = Encode()

    result = job.run(
        dict(type="Heading", depth=3, content=["My heading"]),
        tempdir.getpath("output.md"),
    )
    assert result["result"] is None
    assert result["log"] == []
    assert tempdir.read("output.md").startswith(b"### My heading")
