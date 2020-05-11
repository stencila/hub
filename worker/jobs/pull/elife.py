from .http import pull_http


def pull_elife(source: dict, sink: str) -> str:
    """
    Pull an eLife article.

    Fetches the XML of the article from https://elifesciences.org
    and then walks the XML tree, downloading any graphic media from the 
    elife image server https://iiif.elifesciences.org/
    """
    assert "article" in source, "eLife source must have an article number"

    url = "https://elifesciences.org/articles/{article}.xml".format(**source)
    return pull_http(dict(url=url), sink)
