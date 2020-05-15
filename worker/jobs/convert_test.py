import sys

import pytest

from .convert import Convert


def test_bad_args():
    job = Convert()

    for args, message in [
        [["", None], "input must be a non-empty string or bytes"],
        [["input", {}], "output must be a string or list of strings"],
        [["input", "output", ""], "options must be a dictionary"],
    ]:
        with pytest.raises(AssertionError) as excinfo:
            job.do(*args)
        assert message in str(excinfo.value)


@pytest.mark.skipif(sys.platform != "linux", reason="flakey on other platforms")
def test_simple(tempdir):
    """A simple Markdown to HTML conversion."""
    job = Convert()

    def update_state(state, meta):
        assert state == "RUNNING"

    job.update_state = update_state

    tempdir.write("input.md", b"# Hello\n\nworld!")
    result = job.run(
        tempdir.getpath("input.md"),
        tempdir.getpath("output.html"),
        dict(standalone=False),
    )
    assert result["result"] is None
    assert result["log"] == []
    assert tempdir.read("output.html").startswith(
        b'<article itemscope="" itemtype="http://schema.org/Article" data-itemscope="root">'
    )


def test_multiple_outputs(tempdir):
    """Can pass a list of output files."""
    job = Convert()

    def update_state(state, meta):
        assert state == "RUNNING"

    job.update_state = update_state

    job.run(
        "Some markdown",
        [tempdir.getpath("file1.json"), tempdir.getpath("file2.yaml")],
        {"from": "md"},
    )
    tempdir.compare(["file1.json", "file2.yaml"])
