import asyncio
import html
import os
import re
import shutil
from base64 import b64encode

from django.core.exceptions import ViewDoesNotExist
from django.urls import URLPattern, URLResolver
from django.utils.text import slugify
from pyppeteer import launch

# Paths to include (additional to those that are autodiscovered from root urlpatterns)
INCLUDE = [
    # Render these templates instead of testing the pages (and getting non-200 responses)
    "stencila/render?template=403.html",
    "stencila/render?template=404.html",
    "stencila/render?template=500.html",
]

# Regex, string pairs for replacing URL parameters
REPLACE = [
    (r"<slug:account>", "biotech-corp"),
    (r"<slug:team>", "first-team"),
    (r"<slug:project>", "first-project"),
]

# Regexes of paths to exclude
EXCLUDE = [
    r"^api/.+",
    r"^debug",
    r"^favicon.ico",
    r"^stencila/admin",
    # Anything which still has a URL parameter
    # in it after REPLACE is applied
    r"\?P<",
    r"<[a-z]+:[a-z]+>",
    # Social auth login pages expected to fail because
    # app tokens not available during development
    r"^me/[a-z]+/login/",
    # These pages are not expected to return 200 responses
    r"^stencila/test/403",
    r"^stencila/test/404",
    r"^stencila/test/500",
]

# Regexes of paths to visit as particular user/s.
# First matching regex is used.
# Can be a list of users.
USERS = [
    # Do not authenticate for these:
    [r"^me/(signin|signup)/", "anon"],
    # Defaults to authenticating as `owner` user
    [r".*", "owner"],
]

# Regexes of paths to the CSS selectors on that page that should
# be snapped.
ELEMS = [
    # Organizations
    [r"^orgs/$", ["button.is-primary"]],
    [
        r"^orgs/new/$",
        ["[data-label=name-field]", "[data-label=profile-fields]", "button.is-primary"],
    ],
    [
        r"^[^/]+/settings/$",
        [
            ".menu",
            "[data-label=profile-form]",
            "[data-label=image-form]",
            "[data-label=content-form]",
        ],
    ],
    [r"^[^/]+/users/$", [".menu", "form"]],
    [r"^projects/new/$", ["form", "button.is-primary"]],
]


# Viewport sizes to take screenshots at
VIEWPORTS = [
    # Mobile
    (360, 640),
    # Desktop
    (1920, 1080),
]


def showPath(path):
    return "index" if (path == "" or path == "/") else path


def run(*args):
    """Create screenshots of pages."""
    asyncio.get_event_loop().run_until_complete(main())


async def main():
    """Take screenshots of each path, for each user and of each element (if specified)."""
    shutil.rmtree("snaps")
    os.mkdir("snaps")

    paths = [
        # path for (_, path, _) in extract_views_from_urlpatterns(urlpatterns)
    ] + INCLUDE

    for (regex, string) in REPLACE:
        paths = [re.sub(regex, string, path) for path in paths]

    paths = sorted(set(paths))

    results = []
    browser = await launch()

    for idx, path in enumerate(paths):

        # Check if this path should be excluded
        exclude = False
        for regex in EXCLUDE:
            if re.search(regex, path):
                exclude = True
                break
        if exclude:
            print("{0}/{1} Skipping: {2}".format(idx, len(paths), showPath(path)))
            continue

        page = await browser.newPage()

        # Get the list of users to visit this page as
        users = None
        for regex, users in USERS:
            if re.search(regex, path):
                break
        assert users is not None, "Misconfiguration: USERS should have a catchall regex"
        if not isinstance(users, list):
            users = [users]

        # Visit page as each user
        for user in users:
            print(
                "{0}/{1} Snapping: {2} as {3}".format(
                    idx, len(paths), showPath(path), user
                )
            )

            # Authenticate if necessary
            if user != "anon":
                header = "Basic " + b64encode("{0}:{0}".format(user).encode()).decode()
                await page.setExtraHTTPHeaders({"Authorization": header})

            url = "http://localhost:8000/{}".format(path)
            response = await page.goto(url)

            # Hide debug toolbar unless there was an error
            if response.status == 200:
                await page.addStyleTag(
                    {"content": "#djDebug { display: none !important; }"}
                )

            # Snapshot the page
            snaps = await snap(page, path, user)

            # Snapshot elements within the page
            selectors = None
            for regex, selects in ELEMS:
                if re.search(regex, path):
                    selectors = selects
                    break
            snips = []
            if selectors:
                if not isinstance(selectors, list):
                    selectors = [selectors]
                for selector in selectors:
                    print("{0}/{1} Snipping: {2}".format(idx, len(paths), selector))
                    file = await snip(page, path, user, selector)
                    snips.append(file)

            results.append([path, url, response.status, snaps, snips])

    await browser.close()

    report(results)


async def snap(page, path, user):
    """Take screenshots of the entire page at various viewport sizes."""
    files = []
    for (width, height) in VIEWPORTS:
        file = (
            slugify(
                "{path}-{user}-{width}x{height}".format(
                    path=showPath(path).replace("/", "-"),
                    user=user,
                    width=width,
                    height=height,
                )
            )
            + ".png"
        )
        await page.setViewport(dict(width=width, height=height, deviceScaleFactor=1,))
        await page.screenshot({"path": os.path.join("snaps", file)})
        files.append(file)

    return files


async def snip(page, path, user, selector):
    """Take screenshot of a particular element in the page."""
    file = (
        slugify(
            "{path}-{user}-{selector}".format(
                path=showPath(path).replace("/", "-"), user=user, selector=selector
            )
        )
        + ".png"
    )

    element = await page.querySelector(selector)
    if element:

        await element.screenshot({"path": os.path.join("snaps", file)})

    return file


def report(results):
    """Create a HTML report."""
    report = """
    <style>
        body {
            font-family: Consolas, monospace;
            padding: 25px;
        }
        table {
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #eee;
        }
        td {
            padding: 1em;
        }
        img {
            max-width: 500px;
            max-height: 400px;
            margin: 50px;
            box-shadow:
                0 0.7px 2.2px rgba(0, 0, 0, 0.02),
                0 1.6px 5.3px rgba(0, 0, 0, 0.028),
                0 3px 10px rgba(0, 0, 0, 0.035),
                0 5.4px 17.9px rgba(0, 0, 0, 0.042),
                0 10px 33.4px rgba(0, 0, 0, 0.05),
                0 24px 80px rgba(0, 0, 0, 0.07);
        }
    </style>
    <table>"""
    for (path, url, status, snaps, snips) in results:
        report += """
            <tr>
                <td><a href="{url}" target="_blank">{path}</a></td>
                <td>{status}</td>
                {snaps}
                <td>{snips}</td>
            </tr>
        """.format(
            url=url,
            path=html.escape(showPath(path)),
            status=status,
            snaps="".join(
                [
                    '<td><a href="{0}" target="_blank"><img src="{0}" loading="lazy"></td>'.format(
                        file
                    )
                    for file in snaps
                ]
            ),
            snips="".join(
                [
                    '<a href="{0}" target="_blank"><img src="{0}" loading="lazy">'.format(
                        file
                    )
                    for file in snips
                ]
            ),
        )
    with open("snaps/index.html", "w") as file:
        file.write(report)


def extract_views_from_urlpatterns(urlpatterns, base="", namespace=None):
    """
    Return a list of views from a list of urlpatterns.

    Each object in the returned list is a three-tuple:
    (view_func, regex, name).

    This function was extracted from:
    https://github.com/django-extensions/django-extensions/blob/master/django_extensions/management/commands/show_urls.py
    """
    views = []
    for p in urlpatterns:
        if isinstance(p, URLPattern):
            try:
                if not p.name:
                    name = p.name
                elif namespace:
                    name = "{0}:{1}".format(namespace, p.name)
                else:
                    name = p.name
                pattern = str(p.pattern)
                views.append((p.callback, base + pattern, name))
            except ViewDoesNotExist:
                continue
        elif isinstance(p, URLResolver):
            try:
                patterns = p.url_patterns
            except ImportError:
                continue
            if namespace and p.namespace:
                _namespace = "{0}:{1}".format(namespace, p.namespace)
            else:
                _namespace = p.namespace or namespace
            pattern = str(p.pattern)
            views.extend(
                extract_views_from_urlpatterns(
                    patterns, base + pattern, namespace=_namespace
                )
            )
        elif hasattr(p, "_get_callback"):
            try:
                views.append((p._get_callback(), base + str(p.pattern), p.name))
            except ViewDoesNotExist:
                continue
        elif hasattr(p, "url_patterns") or hasattr(p, "_get_url_patterns"):
            try:
                patterns = p.url_patterns
            except ImportError:
                continue
            views.extend(
                extract_views_from_urlpatterns(
                    patterns, base + str(p.pattern), namespace=namespace
                )
            )
        else:
            raise TypeError("%s does not appear to be a urlpattern object" % p)
    return views
