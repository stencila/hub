import requests


def pull_http(source: dict, sink: str) -> str:
    """
    Pull a file from an HTTP source.
    """
    assert "url" in source, "HTTP source must have a URL"

    session = requests.Session()
    session.max_redirects = 5

    with session.get(source["url"], stream=True, allow_redirects=True) as response:
        with open(sink, "wb") as file:
            for chunk in response:
                file.write(chunk)

    return sink
