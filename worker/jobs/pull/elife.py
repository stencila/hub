import io
import os
import re
import requests
from typing import List

from lxml import etree

from .base import HttpSession


def pull_elife(source: dict, project: str, path: str) -> List[str]:
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
    os.makedirs(os.path.join(project, "{}.media".format(xml)), exist_ok=True)

    # Get the figures and rewrite hrefs
    media_files = []
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
        session.pull(url, os.path.join(project, folder, new_href))

        media_files.append(os.path.join(folder, new_href))

    tree.write(open(os.path.join(project, folder, xml), "wb"))

    return [xml] + media_files
