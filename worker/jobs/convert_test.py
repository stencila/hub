import sys

import pytest

from util.working_directory import working_directory

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

    tempdir.write("input.md", b"# Hello\n\nworld!")
    result = job.run(
        tempdir.getpath("input.md"),
        tempdir.getpath("output.html"),
        dict(standalone=False),
    )
    assert result["log"] == []
    assert tempdir.read("output.html").startswith(
        b'<article itemscope="" itemtype="http://schema.org/Article" data-itemscope="root">'
    )


def test_multiple_outputs(tempdir):
    """Can pass a list of output files."""
    job = Convert()

    job.run(
        "Some markdown",
        [tempdir.getpath("file1.json"), tempdir.getpath("file2.yaml")],
        {"from": "md"},
    )
    tempdir.compare(["file1.json", "file2.yaml"])


# To re-record this test, get a new Google token (e.g. via https://developers.google.com/oauthplayground),
# paste it in below, ensure that the Google account has access to the documents
# being accessed, and run
#   ./venv/bin/pytest --record-mode=rewrite jobs/convert_test.py

ACCESS_TOKEN = "XXXXXXX"


@pytest.mark.vcr
def test_to_gdoc(tempdir):
    with working_directory(tempdir.path):
        with open("input.md", "w") as file:
            file.write("Hello world!")

        job = Convert()
        result = job.run(
            input="input.md",
            output="output.gdoc",
            secrets=dict(access_token=ACCESS_TOKEN),
        )

    tempdir.compare(["input.md", "output.gdoc"])
    assert (
        result["result"]["output.gdoc"]["mimetype"]
        == "application/vnd.google-apps.document"
    )
