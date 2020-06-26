import pytest

from .elife import pull_elife


@pytest.mark.vcr
def test_ok(tempdir):
    files = pull_elife({"article": 45187}, tempdir.path, "45187.jats.xml")

    file_paths = ["45187.jats.xml"] + [
        "45187.jats.xml.media/{0}".format(fig)
        for fig in [
            "fig1.jpg",
            "fig1-figsupp1.jpg",
            "fig1-figsupp2.jpg",
            "fig1-figsupp3.jpg",
            "fig1-figsupp4.jpg",
            "fig1-figsupp5.jpg",
            "fig2.jpg",
            "fig3.jpg",
            "fig4.jpg",
            "fig4-figsupp1.jpg",
            "fig4-figsupp2.jpg",
            "fig5.jpg",
            "fig5-figsupp1.jpg",
            "fig6.jpg",
            "fig6-figsupp1.jpg",
            "fig6-figsupp2.jpg",
            "fig7.jpg",
            "fig7-figsupp1.jpg",
            "fig8.jpg",
            "fig8-figsupp1.jpg",
            "resp-fig1.jpg",
            "resp-fig2.jpg",
            "resp-fig3.jpg",
            "resp-fig4.jpg",
            "resp-fig5.jpg",
            "resp-fig6.jpg",
            "resp-fig7.jpg",
            "resp-fig8.jpg",
            "resp-fig9.jpg",
        ]
    ]

    assert files["45187.jats.xml"]["mimetype"] == "application/xml"
    assert files["45187.jats.xml.media/fig1.jpg"]["mimetype"] == "image/jpeg"

    assert sorted(files.keys()) == sorted(file_paths)

    tempdir.compare(file_paths + ["45187.jats.xml.media/"])


def test_missing_article(tempdir):
    with pytest.raises(AssertionError) as excinfo:
        pull_elife({}, tempdir, "temp.jats.xml")
    assert "source must have an article number" in str(excinfo.value)
