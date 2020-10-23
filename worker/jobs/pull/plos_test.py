import pytest

from util.working_directory import working_directory

from .plos import pull_plos


@pytest.mark.vcr
def test_ok(tempdir):
    with working_directory(tempdir.path):
        files = pull_plos(
            {"article": "10.1371/journal.pcbi.1007273"}, "pcbi.1007273.jats.xml",
        )

    expected = ["pcbi.1007273.jats.xml", "pcbi.1007273.jats.xml.media/"] + [
        "pcbi.1007273.jats.xml.media/" + image
        for image in [
            "e001.png",
            "e002.png",
            "e003.png",
            "e004.png",
            "e005.png",
            "e006.png",
            "g001.png",
            "g002.png",
            "g003.png",
            "g004.png",
            "g005.png",
            "g006.png",
            "g007.png",
            "g008.png",
            "t001.png",
            "t002.png",
        ]
    ]

    assert files["pcbi.1007273.jats.xml"]["mimetype"] == "application/jats+xml"
    assert files["pcbi.1007273.jats.xml.media/e001.png"]["mimetype"] == "image/png"

    tempdir.compare(expected)
