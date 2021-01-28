import asyncio
import html
import os
import re
import shutil
import sys
from base64 import b64encode

from django.core.exceptions import ViewDoesNotExist
from django.urls import URLPattern, URLResolver
from django.utils.text import slugify
from PIL import Image, ImageFilter
from pyppeteer import launch

from manager.urls import urlpatterns

# Paths to include (additional to those that are autodiscovered from root urlpatterns)
INCLUDE = (
    [
        # View of a personal account
        # In REPLACE below we use `an-org` for <slug:account>.
        # This ensures we snap a page for a personal account too
        "a-user/",
        # Simulation of content and error messages served on
        # account subdomains
        "content?account=an-org",  # No project specified -> redirected to account page
        "content/first-project?account=an-org&should-404",  # Project without a snapshot -> error page
        "content/first-project/v42?account=an-org&should-404",  # Bad snapshot id -> error page
        "content/zoo?account=an-org&should-404",  # Non existent project -> error page
    ]
    + [
        # Forms for creating new sources
        # These pages are used below in `ELEMS`
        "an-org/first-project/sources/new/%s" % type
        for type in [
            "github",
            "googledocs",
            "googlesheets",
            "googledrive",
            "url",
            "elife",
            "plos",
        ]
    ]
    + [
        # Render these templates instead of testing the pages (and getting non-200 responses)
        "stencila/render?template=403.html",
        "stencila/render?template=404.html",
        "stencila/render?template=500.html",
    ]
)

# Regex, string pairs for replacing URL parameters
REPLACE = [
    (r"<slug:account>", "an-org"),
    (r"<slug:team>", "first-team"),
    (r"<slug:project>", "first-project"),
    (r"\(\?P<source>\.\+\??\)", "upload://main.md"),
    (r"\(\?P<file>\.\+\?\)", "main.md"),
]

# Regexes of paths to exclude
EXCLUDE = [
    r"^api/.+",
    r"^debug",
    # Non-HTML responses
    r"^favicon.ico",
    r"^robots.txt",
    r"^stencila/admin",
    # Anything which still has a URL parameter
    # in it after REPLACE is applied
    r"\?P<",
    r"<[a-z]+:[a-z]+>",
    # Social auth login pages expected to fail because
    # app tokens not available during development
    r"^me/[a-z]+/login/",
    # Non-GET URLs
    r"[^/]+/profile/image",
    # Redirects to external pages
    r"[^/]+/billing",
    # These pages are not expected to return 200 responses
    r"^stencila/test/403",
    r"^stencila/test/404",
    r"^stencila/test/500",
]

# Regexes of paths to visit as particular user/s.
# First matching regex is used.
# Can be a list of users, in which case, any "anon"
# item must come first.
USERS = [
    # Do not authenticate for these:
    [r"^me/(signin|signup)/", "anon"],
    # Visit index as `anon` and `a-user`
    [r"^/$", ["anon", "a-user"]],
    # Visit `a-user`'s account page as `anon`, `a-user`, and `member` (who
    # will be a member of all their projects)
    [r"^a-user/", ["anon", "a-user", "member"]],
    # Defaults to authenticating as `owner` user
    [r".*", "owner"],
]


# Expected response status codes other than 200
STATUS = [
    # Above we mark some paths with...
    [r"&should-404", 404]
]


def elem(name: str, selector: str, parent: str = None, padding: int = 50):
    return dict(name=name, selector=selector, parent=parent, padding=padding)


# Regexes of paths to the CSS selectors on that page that should
# be snapped.
ELEMS = [
    # fmt: off

    #
    # Users
    #
    [
        r"^me/signin/$",
        [
            elem("user-signin-social-buttons", "main .buttons"),
            elem("user-signin-username-password-form", "form")
        ],
    ],
    [
        r"^me/signup/$",
        [
            elem("user-signup-form", "form"),
        ],
    ],

    #
    # Organizations
    #
    [
        r"^orgs/$",
        [
            elem("org-new-button", "a.is-primary"),
            elem("org-search", ".field")
        ],
    ],
    [
        r"^orgs/new/$",
        [
            elem("org-new-name-field", "#name-field"),
            elem("org-new-profile-fields", "#profile-fields"),
            elem("org-new-create-button", "button.is-primary"),
        ],
    ],
    [
        r"^an-org/profile/$",
        [
            elem("org-settings-menu-item", "#menu-item-settings", ".menu", padding=20),
            elem("org-settings-profile", "#profile-form"),
            elem("org-settings-image-form", "#image-form"),
        ],
    ],
    [
        r"^an-org/publishing/$",
        [
            elem("org-settings-theme-field", "label[for=theme] + .control"),
            elem("org-settings-hosts-field", "label[for=hosts] + .control"),
        ],
    ],
    [
        r"^an-org/users/$",
        [
            elem("org-users-menu-item", "#menu-item-users", ".menu", 20),
            elem("org-users-add-user", "form"),
            elem("org-users-change-user", "#accounts-users-list .field"),
        ],
    ],

    #
    # Projects
    #
    [
        r"^projects/$",
        [
            elem("project-new-button", "a.is-primary")
        ]
    ],
    [
        r"^projects/new/$",
        [
            elem("project-new-account-field", "#account"),
            elem("project-new-name-field", "label[for=name] + .control"),
            elem("project-new-public-field", ".field:last-of-type"),
            elem("project-new-create-button", "button.is-primary")
        ]
    ],
    [
        r"^an-org/first-project/sources/$",
        [
            elem("project-sources-menu-item", "#menu-item-sources", ".menu", padding=20),
            elem("project-sources-new-button", "button.is-primary"),
        ],
    ],
    [
        r"^an-org/first-project/sources/new/elife$",
        [
            elem("project-sources-new-elife", "form"),
            # These are common elements to all new source pages
            # so we just create snaps for them once here.
            elem("project-sources-new-path-field", ".field:last-of-type", padding=15),
            elem("project-sources-new-create-button", "button.is-primary", padding=15),
        ]
    ],
    [
        r"^an-org/first-project/sources/new/github$",
        [
            elem("project-sources-new-github", "form"),
            elem("project-sources-new-github-url", "form fieldset:first-of-type"),
            elem("project-sources-new-github-repo", "form fieldset:last-of-type"),
        ]
    ],
    [
        r"^an-org/first-project/sources/new/googledrive$",
        [
            elem("project-sources-new-googledrive", "form"),
            elem("project-sources-new-googledrive-url", "form fieldset:first-of-type"),
            elem("project-sources-new-googledrive-id", "form fieldset:last-of-type"),
        ]
    ],
    [
        r"^an-org/first-project/sources/new/googledocs$",
        [
            elem("project-sources-new-googledocs", "form"),
        ]
    ],
    [
        r"^an-org/first-project/sources/new/googlesheets$",
        [
            elem("project-sources-new-googlesheets", "form"),
        ]
    ],
    [
        r"^an-org/first-project/sources/new/plos$",
        [
            elem("project-sources-new-plos", "form"),
        ]
    ],
    [
        r"^an-org/first-project/sources/new/url$",
        [
            elem("project-sources-new-url", "form"),
        ]
    ],
    [
        r"^an-org/first-project/sources/upload$",
        [
            elem("project-sources-new-upload", "form", padding=75),
        ]
    ],
    [
        r"^an-org/first-project/settings/$",
        [
            elem("project-settings-menu-item", "#menu-item-settings", ".menu", padding=20),
            elem("project-settings-name-field", "label[for=name] + .control"),
            elem("project-settings-title-field", "label[for=title] + .control"),
            elem("project-settings-description-field", "label[for=description] + .control"),
            elem("project-settings-liveness-field", "label[for=liveness] + .control"),
            elem("project-settings-pinned-field", "label[for=pinned] + .control"),
            elem("project-settings-theme-field", "label[for=theme] + .control"),
            elem("project-settings-delete-form", "form[hx-delete]"),
        ],
    ],
    [
        r"^an-org/first-project/sharing/$",
        [
            elem("project-sharing-menu-item", "#menu-item-sharing", ".menu", padding=20),
            elem("project-sharing-public", "label[for=public-toggle]", padding=5),
            elem("project-sharing-add-agent", "form"),
            elem("project-sharing-change-agent", "#projects-agents-list .field"),
        ],
    ],
    # fmt: on
]


# Viewport sizes to take screenshots at
VIEWPORTS = [
    # Mobile
    (360, 640),
    # Desktop
    (1920, 1080),
]


def run(*args):
    """Create screenshots of pages."""
    asyncio.get_event_loop().run_until_complete(main())


async def main():
    """Take screenshots of each path, for each user and of each element (if specified)."""
    if os.path.exists("snaps"):
        shutil.rmtree("snaps")
    os.mkdir("snaps")

    paths = [
        path for (_, path, _) in extract_views_from_urlpatterns(urlpatterns)
    ] + INCLUDE

    for (regex, string) in REPLACE:
        paths = [re.sub(regex, string, path) for path in paths]

    paths = sorted(set(paths))

    errors = 0
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
            print(
                "{0}/{1} {3}Skipping: {2}{4}".format(
                    idx, len(paths), showPath(path), colors.DEBUG, colors.RESET
                )
            )
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
                "{0}/{1} {4}Snapping{5}: {2} as {3}".format(
                    idx, len(paths), showPath(path), user, colors.OK, colors.RESET
                ),
                end=":",
            )

            # Authenticate if necessary
            if user != "anon":
                header = "Basic " + b64encode("{0}:{0}".format(user).encode()).decode()
                await page.setExtraHTTPHeaders({"Authorization": header})

            url = "http://localhost:8000/{}".format(path)
            response = await page.goto(url)

            # Grab data from the debug toolbar
            data = await page.evaluate(
                """() => {
                const cpu_time = document.querySelector('#djDebug .TimerPanel small ')
                                         .innerText
                                         .match(/[0-9.]+/)[0]
                const db_queries = document.querySelector('#djDebug .SQLPanel small')
                                           .innerText
                                           .match(/[0-9]+/)[0]
                return { cpu_time, db_queries }
            }"""
            )

            # Get expect response code
            status = 200
            for regex, elems in STATUS:
                if re.search(regex, path):
                    status = elems
                    break

            # Hide debug toolbar unless there was an error
            if response.status == status:
                print(" {0}✔️{1}".format(colors.OK, colors.RESET))
                await page.addStyleTag(
                    {"content": "#djDebug { display: none !important; }"}
                )
            else:
                print(" {0}❌{1}".format(colors.ERROR, colors.RESET))
                errors += 1

            # Snapshot the page
            snaps = await snap(page, path, user)

            # Snapshot elements within the page
            elements = None
            for regex, elems in ELEMS:
                if re.search(regex, path):
                    elements = elems
                    break
            snips = []
            if elements:

                # Take element screenshots in a narrowish viewport so that
                # they are not too wide.
                await page.setViewport(
                    dict(width=850, height=5000, deviceScaleFactor=1,)
                )

                # Add styles for snips
                await page.addStyleTag(
                    dict(
                        content="""
                    .snipTarget {
                        position: relative;
                        z-index: 300;
                    }

                    #snipBackdrop {
                        background-color: #efefef;
                        opacity: 0.5;
                        content: '';
                        height: 100vh;
                        left: 0;
                        position: fixed;
                        top: 0;
                        width: 100vw;
                        z-index: 200;
                    }
                """
                    )
                )

                # Add function for setting the class for the target element
                # adding a backdrop, and returning the snipshot rectangle
                await page.evaluate(
                    """
                window.snip = (selector, parentSelector, padding) => {
                    const el = document.querySelector(selector)
                    if (el == null) return null;

                    const target = document.querySelector('.snipTarget')
                    if (target != null) {
                        target.classList.remove('snipTarget')
                    }
                    el.classList.add('snipTarget')

                    let backdrop = document.querySelector('#snipBackdrop')
                    if (backdrop === null) {
                        backdrop = document.createElement('span')
                        backdrop.id = 'snipBackdrop'
                        document.body.append(backdrop)
                    }

                    let box = el
                    if (parentSelector) {
                        box = document.querySelector(parentSelector)
                        if (box === null) box = el
                    }

                    let { x, y, width, height } = box.getBoundingClientRect()
                    x = Math.max(x - padding, 0)
                    y = Math.max(y - padding, 0)
                    width = Math.min(width + 2 * padding, window.innerWidth - x)
                    height = height + 2 * padding
                    return { x, y, width, height }
                }
                """
                )

                for element in elements:
                    print(
                        "{0}/{1} {3}Snipping{4}: {2}".format(
                            idx, len(paths), element["name"], colors.INFO, colors.RESET
                        ),
                        end=":",
                    )
                    file = await snip(page, path, user, element)
                    if file:
                        print(" {0}✔️{1}".format(colors.OK, colors.RESET))
                        snips.append(file)
                    else:
                        print(" {0}❌{1}".format(colors.ERROR, colors.RESET))
                        errors += 1

            results.append([path, url, user, response.status, data, snaps, snips])

    await browser.close()

    report(results)

    if errors > 0:
        print("\n\n{1}Errors{2}: {0}".format(errors, colors.ERROR, colors.RESET))
        sys.exit(errors)


def showPath(path):
    return "index" if (path == "" or path == "/") else path


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
            ).strip("-")
            + ".png"
        )
        await page.setViewport(dict(width=width, height=height, deviceScaleFactor=1,))
        await page.screenshot({"path": os.path.join("snaps", file)})
        files.append(file)

    return files


async def snip(page, path, user, element):
    """Take screenshot of a particular element in the page."""
    rect = await page.evaluate(
        "window.snip", element["selector"], element["parent"], element["padding"],
    )
    if rect:
        file = element["name"] + ".png"
        path = os.path.join("snaps", file)

        # Screenshot it
        await page.screenshot({"clip": rect, "path": path})

        # Add drop shadow to the file
        image = Image.open(path)
        image = addShadow(image)
        image.save(path)

        return file
    else:
        return None


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
        .tag {
            display: inline-block;
            margin: 5px;
            padding: 5px;
            border-radius: 5px;
            font-size: 0.75rem;
        }
    </style>
    <table>"""
    for (path, url, user, status, data, snaps, snips) in results:
        cpu = float(data.get("cpu_time", ""))
        db = float(data.get("db_queries", ""))

        report += """
            <tr>
                <td>
                    <a href="{url}" target="_blank">{path}</a>
                    as <strong>{user}</strong>
                </td>
                <td>
                    <span class="tag" style="background-color: {status_color}">
                        {status}
                    </span>
                    <span class="tag" style="background-color: hsl(0, 80%, 50%, {cpu_alpha})">
                        {cpu} ms
                    </span>
                    <span class="tag" style="background-color: hsl(0, 80%, 50%, {db_alpha})">
                        {db} queries
                    </span>
                </td>
                {snaps}
                <td>{snips}</td>
            </tr>
        """.format(
            url=url,
            path=html.escape(showPath(path)),
            user=user,
            status=status,
            status_color="#d9ffb0" if status == 200 else "#ffb4b0",
            cpu=cpu,
            cpu_alpha=min(max((cpu - 100) / 1000, 0), 1),
            db=db,
            db_alpha=min(max(db / 10, 0), 1),
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


class colors:
    DEBUG = "\033[90m"
    OK = "\033[92m"
    INFO = "\033[94m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    RESET = "\033[0m"


def addShadow(
    image,
    iterations=10,
    border=30,
    offset=[4, 4],
    backgroundColour="white",
    shadowColour="#999",
):
    """
    Add a drop shadown to an image

    image: base image to give a drop shadow
    iterations: number of times to apply the blur filter to the shadow
    border: border to give the image to leave space for the shadow
    offset: offset of the shadow as [x,y]
    backgroundCOlour: colour of the background
    shadowColour: colour of the drop shadow

    From https://en.wikibooks.org/wiki/Python_Imaging_Library/Drop_Shadows
    """

    # Calculate the size of the shadow's image
    fullWidth = image.size[0] + abs(offset[0]) + 2 * border
    fullHeight = image.size[1] + abs(offset[1]) + 2 * border

    # Create the shadow's image. Match the parent image's mode.
    shadow = Image.new(image.mode, (fullWidth, fullHeight), backgroundColour)

    # Place the shadow, with the required offset
    shadowLeft = border + max(offset[0], 0)  # if <0, push the rest of the image right
    shadowTop = border + max(offset[1], 0)  # if <0, push the rest of the image down
    # Paste in the constant colour
    shadow.paste(
        shadowColour,
        [shadowLeft, shadowTop, shadowLeft + image.size[0], shadowTop + image.size[1]],
    )

    # Apply the BLUR filter repeatedly
    for i in range(iterations):
        shadow = shadow.filter(ImageFilter.BLUR)

    # Paste the original image on top of the shadow
    imgLeft = border - min(offset[0], 0)  # if the shadow offset was <0, push right
    imgTop = border - min(offset[1], 0)  # if the shadow offset was <0, push down
    shadow.paste(image, (imgLeft, imgTop))

    return shadow
