import io
import os
import re
import shutil
from typing import List, Optional

import requests
from lxml import etree

from util.files import Files, file_info

from .helpers import HttpSession


def pull_elife(source: dict, path: Optional[str] = None, **kwargs) -> Files:
    """
    Pull an eLife article.

    Fetches the XML of the article from https://elifesciences.org
    and then walks the XML tree, downloading any graphic media from the
    elife image server https://iiif.elifesciences.org/
    """
    assert "article" in source, "eLife source must have an article number"

    article = source["article"]

    if not path:
        path = f"elife-{article}.xml"

    folder, file = os.path.split(path)

    files = {}
    session = HttpSession()

    # Get the article JATS XML
    response = session.fetch_url(f"https://elifesciences.org/articles/{article}.xml")
    tree = etree.parse(io.BytesIO(response.content))
    root = tree.getroot()
    xlinkns = "http://www.w3.org/1999/xlink"

    # Get the figures and rewrite hrefs
    for graphic in root.iterdescendants(tag="graphic"):
        href = graphic.attrib.get("{%s}href" % xlinkns)
        if not href.startswith("elife"):
            continue
        if not href.endswith(".tif"):
            href += ".tif"

        url = f"https://iiif.elifesciences.org/lax:{article}%2F{href}/full/600,/0/default.jpg"
        image_name = href.replace(f"elife-{article}-", "")
        image_name = re.sub(r"-v\d+\.tif$", ".jpg", image_name)
        new_href = f"{file}.media/{image_name}"
        image_path = os.path.join(folder, new_href)

        os.makedirs(os.path.join(folder, f"{file}.media"), exist_ok=True)
        session.pull(url, image_path)

        graphic.attrib["{%s}href" % xlinkns] = new_href
        graphic.attrib["mime-subtype"] = "jpeg"

        files[image_path] = file_info(image_path)

    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
    tree.write(open(path, "wb"))
    files[path] = file_info(path, mimetype="application/jats+xml")

    return files
