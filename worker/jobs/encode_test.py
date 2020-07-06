import pytest

from .encode import Encode


@pytest.mark.skip(reason="Failing test for currently non-essential job")
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
