import io
import os
import re
import requests
from typing import List

from lxml import etree

from .helpers import HttpSession, Files, begin_pull, end_pull


def pull_elife(source: dict, working_dir: str, path: str) -> Files:
    """
    Pull an eLife article.

    Fetches the XML of the article from https://elifesciences.org
    and then walks the XML tree, downloading any graphic media from the
    elife image server https://iiif.elifesciences.org/
    """
    assert "article" in source, "eLife source must have an article number"

    url = "https://elifesciences.org/articles/{article}.xml".format(**source)

    folder, xml = os.path.split(path)
    if not xml.endswith(".xml"):
        xml += ".xml"

    session = HttpSession()
    response = session.fetch_url(url)
    tree = etree.parse(io.BytesIO(response.content))
    root = tree.getroot()
    xlinkns = "http://www.w3.org/1999/xlink"

    temporary_dir = begin_pull(working_dir)
    os.makedirs(os.path.join(temporary_dir, "{}.media".format(xml)), exist_ok=True)

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

        new_href = "{}.media/{}".format(xml, filename)
        graphic.attrib["{%s}href" % xlinkns] = new_href
        graphic.attrib["mime-subtype"] = "jpeg"
        session.pull(url, os.path.join(temporary_dir, folder, new_href))

    tree.write(open(os.path.join(temporary_dir, folder, xml), "wb"))

    return end_pull(working_dir, path, temporary_dir)
