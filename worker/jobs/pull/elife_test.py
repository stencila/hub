import pytest

from .elife import pull_elife


def test_ok(tempdir):
    figures = [
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

    pull_elife({"article": 45187}, tempdir.getpath("45187.jats.xml"))
    tempdir.compare(
        ["45187.jats.xml", "45187.jats.xml.media/"]
        + ["45187.jats.xml.media/" + fig for fig in figures]
    )


def test_missing_article(tempdir):
    with pytest.raises(AssertionError) as excinfo:
        pull_elife({}, "temp.jats.xml")
    assert "source must have an article number" in str(excinfo.value)
