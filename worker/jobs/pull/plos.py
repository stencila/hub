import io
import os
import re
import shutil
from pathlib import Path
from typing import List, Optional

from lxml import etree

from util.files import Files, file_info
from util.http import HttpSession


def pull_plos(source: dict, path: Optional[str] = None, **kwargs) -> Files:
    """
    Pull a PLOS article.

    Fetches the XML of the article from https://journals.plos.org
    and then walks the XML tree, downloading any graphic media.
    """
    doi = source.get("article")
    assert doi, "PLOS source must have an article DOI"

    match = re.match(r"^10\.1371\/journal\.([a-z]+)\.(\d+)$", doi or "")
    assert match is not None, "unknown PLOS article format"

    journals = dict(
        pbio="plosbiology",
        pcbi="ploscompbiol",
        pgen="plosgenetics",
        pmed="plosmedicine",
        pntd="plosntds",
        pone="plosone",
        ppat="plospathogens",
    )
    journal = journals.get(match.group(1))
    assert journal, "unknown PLOS journal: {}".format(match.group(1))

    if not path:
        path = f"{journal}-{match.group(2)}.xml"

    folder, file = os.path.split(path)
    Path(folder).mkdir(parents=True, exist_ok=True)

    files = {}
    session = HttpSession()

    # Get the article JATS XML
    response = session.fetch_url(
        f"https://journals.plos.org/{journal}/article/file?id={doi}&type=manuscript"
    )
    tree = etree.parse(io.BytesIO(response.content))
    root = tree.getroot()
    xlinkns = "http://www.w3.org/1999/xlink"

    # Get the figures and rewrite hrefs
    for graphic in root.iterdescendants(tag="graphic"):
        href = graphic.attrib.get("{%s}href" % xlinkns)
        if not href.startswith(f"info:doi/{doi}"):
            continue

        url = f"https://journals.plos.org/{journal}/article/"
        id = href.split(".").pop()
        if id.startswith("e"):  # Equation
            url += f"file?id=info:doi/{doi}.{id}&type=thumbnail"
        else:  # Everything else
            url += f"figure/image?id={doi}.{id}&size=medium"

        image_name = f"{id}.png"
        new_href = f"{file}.media/{image_name}"
        image_path = os.path.join(folder, new_href)

        os.makedirs(os.path.join(folder, f"{file}.media"), exist_ok=True)
        session.pull(url, image_path)

        graphic.attrib["{%s}href" % xlinkns] = new_href
        graphic.attrib["mime-subtype"] = "png"

        files[image_path] = file_info(image_path)

    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
    tree.write(open(path, "wb"))
    files[path] = file_info(path, mimetype="application/jats+xml")

    return files
