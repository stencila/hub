import re

from bs4 import BeautifulSoup


def prettify_html_middleware(get_response):
    """
    HTML code prettification middleware.

    Because debugging templates, in particular template composition and styling,
    is easier if the HTML is pretty!

    Thanks to https://djangosnippets.org/snippets/2279/
    """
    regex = re.compile(r"^(\s*)", re.MULTILINE)

    def middleware(request):
        response = get_response(request)
        if response["Content-Type"].split(";", 1)[0] == "text/html":
            response.content = regex.sub(
                r"\1\1", BeautifulSoup(response.content).prettify()
            )
        return response

    return middleware
