import re
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, reverse
from django.utils import timezone

from accounts.models import Account
from accounts.quotas import AccountQuotas
from jobs.models import JobStatus
from manager import themes
from manager.version import __version__
from projects.models.files import File, FileDownloads
from projects.models.projects import Project, ProjectLiveness
from projects.models.snapshots import Snapshot


def content(
    request: HttpRequest,
    project_name: Optional[str] = None,
    version: Optional[str] = None,
    key: Optional[str] = None,
    file_path: Optional[str] = None,
) -> HttpResponse:
    """
    Serve content on behalf on an account.

    This view is designed to handle all the serving of account content.
    It's the Hub's equivalent of Github Pages which serves content from
    https://<account>.stencila.io/<project>.
    """
    host = request.get_host()
    prod = True
    if (
        settings.CONFIGURATION.endswith("Dev")
        or settings.CONFIGURATION.endswith("Test")
    ) and (host.startswith("127.0.0.1") or host.startswith("localhost")):
        prod = False
        # During development and testing get the account name
        # from a URL parameter
        account_name = request.GET.get("account")
        assert account_name is not None, "Do you need to add `?=account` to URL?"
    else:
        # In production get the account from the request subdomain
        match = re.match(r"^([^.]+)." + settings.ACCOUNTS_DOMAIN, host)

        # Assert that this is NOT the primary domain (we never want to
        # serve account content from there)
        assert match is not None
        assert settings.PRIMARY_DOMAIN not in host

        account_name = match.group(1)

    # Functions for returning special error pages for this request
    #
    # We need to use custom 404's here because the site wide `404.html`
    # assumes to be on hub.stenci.la.
    #
    # These have a context which uses the supplied account name, project name and file
    # path strings to avoid inadvertently leaking info (e.g. about existence
    # of a private project)

    def render_404(template: str):
        return render(
            request,
            template,
            dict(
                account_name=account_name,
                project_name=project_name,
                file_path=file_path,
            ),
            status=404,
        )

    def invalid_account():
        return render_404("accounts/content/404_invalid_account.html")

    def unavailable_project():
        return render_404("accounts/content/404_unavailable_project.html")

    def no_snapshots():
        return render_404("accounts/content/404_no_snapshots.html")

    def invalid_snapshot():
        return render_404("accounts/content/404_invalid_snapshot.html")

    def invalid_file():
        return render_404("accounts/content/404_invalid_file.html")

    # Get the account
    try:
        account = Account.objects.get(name=account_name)
    except Account.DoesNotExist:
        return invalid_account()

    # If no project is specified then redirect to the account's page
    # on the Hub (rather than 404ing).
    # In the future we may allow accounts to specify a default project
    # to serve as a "home" project.
    if not project_name:
        return redirect(
            primary_domain_url(
                request, name="ui-accounts-retrieve", kwargs=dict(account=account_name)
            ),
            permanent=False,
        )

    # If the request is for a project folder, rather than a specific file,
    # then redirect to slash appended URL is necessary to ensure that
    # relative links work OK.
    # Do this here before progressing with any more DB queries
    if not file_path and not request.path.endswith("/"):
        path = request.get_full_path(force_append_slash=True)
        # In prod need to remove the prefix added by Nginx
        if prod and path.startswith("/content/"):
            path = re.sub(r"^/content/", "/", path)
        return redirect(path)

    # Check for project
    try:
        project = Project.objects.get(account=account, name=project_name)
    except Project.DoesNotExist:
        return unavailable_project()

    # Authorize the request
    # This is being served on a domain where we do not know the user.
    # So if the project is not public then a key must be provided in the URL.
    # The key is part of the URL, not a query parameter, so that relative links
    # media files etc do not need to be rewritten.
    if not project.public:
        if key != project.key:
            return unavailable_project()

    # If the URL does not have an explicit version then fallback to project defaults
    if version is None:
        version = project.liveness

    # Default to serving index.html
    if not file_path:
        file_path = "index.html"

    # Should the file be served from the working directory or a snapshot?
    snapshot = None
    if version == ProjectLiveness.LIVE.value:
        try:
            file = File.objects.get(project=project, path=file_path, current=True)
        except File.DoesNotExist:
            return invalid_file()
    else:
        if version == ProjectLiveness.LATEST.value:
            snapshots = project.snapshots.filter(
                job__status=JobStatus.SUCCESS.value
            ).order_by("-created")
            if snapshots:
                snapshot = snapshots[0]
            else:
                return no_snapshots()
        elif version == ProjectLiveness.PINNED.value:
            # Elsewhere there should be checks to ensure the data
            # does not break the following asserts. But these serve as
            # a final check.
            snapshot = project.pinned
            assert (
                snapshot is not None
            ), "Project has liveness `pinned` but is not pinned to a snapshot"
            assert (
                snapshot.project_id == project.id
            ), "Project is pinned to a snapshot for a different project!"
        elif version.startswith("v"):
            match = re.match(r"v(\d+)$", version)
            if match is None:
                return invalid_snapshot()
            number = match.group(1)
            try:
                snapshot = Snapshot.objects.get(project=project, number=number)
            except Snapshot.DoesNotExist:
                return invalid_snapshot()
        else:
            raise ValueError("Invalid version value: " + version)

        # Check that the file exists in the snapshot
        try:
            file = File.objects.get(snapshot=snapshot, path=file_path)
        except File.DoesNotExist:
            return invalid_file()

    # Limit the download rate if the account is over it's download
    # quota for the current month
    if AccountQuotas.FILE_DOWNLOADS_MONTH.reached(account):
        limit_rate = "1000"  # bytes/second
    else:
        limit_rate = "off"

    # Update the download metrics
    month = timezone.now().isoformat()[:7]
    with transaction.atomic():
        if FileDownloads.objects.filter(file=file, month=month).count() == 0:
            FileDownloads.objects.create(file=file, month=month, count=1)
        else:
            FileDownloads.objects.filter(file=file, month=month).update(
                count=F("count") + 1
            )

    # Handle the index.html file specially
    if file.path == "index.html":
        html = file.get_content()
        if snapshot:
            return snapshot_index_html(
                html, request, account=account, project=project, snapshot=snapshot
            )
        else:
            return working_index_html(html, request, account=account, project=project)
    else:
        return file.get_response(limit_rate=limit_rate)


def working_index_html(
    html: bytes, request: HttpRequest, account: Account, project: Project
) -> HttpResponse:
    """
    Get an index.html for a project.
    """
    return index_html(
        account,
        html,
        source_url=primary_domain_url(
            request,
            name="ui-projects-files-list",
            kwargs=dict(account=account.name, project=project.name),
        ),
        session_provider_url=primary_domain_url(
            request, name="api-projects-session", kwargs=dict(project=project.id),
        ),
    )


def snapshot_index_html(
    html: bytes,
    request: HttpRequest,
    account: Account,
    project: Project,
    snapshot: Snapshot,
) -> HttpResponse:
    """
    Get an index.html from a snapshot.
    """
    return index_html(
        account,
        html,
        source_url=primary_domain_url(
            request,
            name="ui-projects-snapshots-retrieve",
            kwargs=dict(
                account=account.name, project=project.name, snapshot=snapshot.number,
            ),
        ),
        session_provider_url=primary_domain_url(
            request,
            name="api-projects-snapshots-session",
            kwargs=dict(project=project.id, snapshot=snapshot.number),
        ),
    )


def index_html(
    account: Account, html: bytes, source_url: str, session_provider_url: str
) -> HttpResponse:
    """
    Augment a index.html file.

    Adds necessary headers and injects content required to
    connect to a session, and monitor errors.
    """
    # Pin the version of Thema to avoid redirects to NPM which can slow
    # page load times down substantially
    html = html.replace(
        b"https://unpkg.com/@stencila/thema@2/dist/themes/",
        "https://unpkg.com/@stencila/thema@{version}/dist/themes/".format(
            version=themes.version
        ).encode(),
    )

    # Add Sentry for error monitoring
    if settings.SENTRY_DSN:
        html = html.replace(
            b"</head>",
            """  <script
        src="https://browser.sentry-cdn.com/5.20.1/bundle.min.js"
        integrity="sha384-O8HdAJg1h8RARFowXd2J/r5fIWuinSBtjhwQoPesfVILeXzGpJxvyY/77OaPPXUo"
        crossorigin="anonymous"></script>
    <script>Sentry.init({{ dsn: '{dsn}', release: 'hub@{version}' }});</script>
  </head>""".format(
                dsn=settings.SENTRY_DSN, version=__version__
            ).encode(),
        )

    # Add a <stencila-executable-document-toolbar> element
    html = html.replace(
        b'data-itemscope="root">',
        """data-itemscope="root">
        <stencila-executable-document-toolbar
            source-url="{source_url}"
            session-provider-url="{session_provider_url}"
        ></stencila-executable-document-toolbar>""".format(
            source_url=source_url, session_provider_url=session_provider_url
        ).encode(),
    )

    response = HttpResponse(html)

    # Add content security headers if the account has `hosts` set
    hosts = account.hosts or ""
    # CSP `frame-ancestors` for modern browers
    response[
        "Content-Security-Policy"
    ] = "frame-ancestors 'self' *.stenci.la {};".format(hosts)
    # `X-Frame-Options` for older browsers (only allows one value, so use first)
    first = hosts.split()[0] if hosts.split() else "*.stenci.la"
    response["X-Frame-Options"] = "allow-from {}".format(first)

    return response


def primary_domain_url(request, name, kwargs):
    """
    Get a URL at the primary domain.

    See also the template tag by the same name.
    """
    url = "{scheme}://{domain}".format(
        scheme="https" if request.is_secure() else "http",
        domain=settings.PRIMARY_DOMAIN,
    )
    return url + reverse(name, kwargs=kwargs)
