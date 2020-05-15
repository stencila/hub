import io
import os
import re
import requests

from lxml import etree

from .base import PullSession


def pull_elife(source: dict, sink: str) -> str:
    """
    Pull an eLife article.

    Fetches the XML of the article from https://elifesciences.org
    and then walks the XML tree, downloading any graphic media from the
    elife image server https://iiif.elifesciences.org/
    """
    assert "article" in source, "eLife source must have an article number"

    url = "https://elifesciences.org/articles/{article}.xml".format(**source)
    folder, article = os.path.split(sink)

    assert "{article}.jats.xml".format(**source) == article

    session = PullSession()
    response = session.fetch_url(url)
    tree = etree.parse(io.BytesIO(response.content))
    root = tree.getroot()
    xlinkns = "http://www.w3.org/1999/xlink"
    os.makedirs("{}.media".format(sink), exist_ok=True)

    # Get the figures and rewrite hrefs
    for graphic in root.iterdescendants(tag="graphic"):
        href = graphic.attrib.get("{%s}href" % xlinkns)
        if not href.startswith("elife"):
            continue
        if not href.endswith(".tif"):
            href += ".tif"

        url = "https://iiif.elifesciences.org/lax:{}%2F{}/full/600,/0/default.jpg".format(
            source["article"], href
        )

        filename = href.replace("elife-{}-".format(source["article"]), "")
        filename = re.sub(r"-v\d+\.tif$", ".jpg", filename)

        new_href = "{}.media/{}".format(article, filename)
        graphic.attrib["{%s}href" % xlinkns] = new_href
        graphic.attrib["mime-subtype"] = "jpeg"
        session.pull(url, "{}/{}".format(folder, new_href))

    tree.write(open(sink, "wb"))

    return sink
