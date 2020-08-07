import re
from typing import Optional

import httpx
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, reverse

from accounts.models import Account
from jobs.models import JobStatus
from projects.models.files import File
from projects.models.projects import Project, ProjectLiveness
from projects.models.snapshots import Snapshot

storage_client = httpx.Client()


def content(
    request: HttpRequest,
    project_name: Optional[str] = None,
    version: Optional[str] = None,
    file_path: Optional[str] = None,
) -> HttpResponse:
    """
    Serve content on behalf on an account.

    This view is designed to handle all the serving of account content.
    It's the Hub's equivalent of Github Pages which serves content from
    https://<account>.stencila.io/<project>.
    """
    host = request.get_host()
    if (
        settings.CONFIGURATION.endswith("Dev")
        or settings.CONFIGURATION.endswith("Test")
    ) and (host.startswith("127.0.0.1") or host.startswith("localhost")):
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
            "{scheme}://{domain}:{port}/{account}".format(
                scheme="https" if request.is_secure() else "http",
                domain=settings.PRIMARY_DOMAIN,
                port=request.get_port(),
                account=account,
            )
        )

    # If the request is for a project folder, rather than a specific file,
    # then redirect to slash appended URL is necessary to ensure that
    # relative links work OK.
    # Do this here before progressing with any more DB queries
    if not file_path and not request.path.endswith("/"):
        return redirect(request.get_full_path(force_append_slash=True))

    # Check for project
    try:
        project = Project.objects.get(account=account, name=project_name)
    except Project.DoesNotExist:
        return unavailable_project()

    # Authorize the request
    # This is being served on a domain where we do not know the user.
    # So if the project is not public then a key must be provided in the URL
    if not project.public:
        key = request.GET.get("key")
        if key != project.key:
            return unavailable_project()

    # If the URL does not have an explicit version then fallback to project defaults
    if version is None:
        version = project.liveness

    # Which snapshot or working directory to serve from?
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

    # Default to serving index.html
    if not file_path:
        file_path = "index.html"

    # Check that the file exists in the snapshot
    # Is DB query necessary, or can we simply rely on upstream 404ing ?
    try:
        File.objects.get(snapshot=snapshot, path=file_path)
    except File.DoesNotExist:
        return invalid_file()

    # Handle the index.html file specially
    if file_path == "index.html":
        return snapshot_index_html(
            request, account=account, project=project, snapshot=snapshot
        )

    # Redirect to other files
    url = snapshot.file_url(file_path)
    if settings.CONFIGURATION.endswith("Dev"):
        # During development just do a simple redirect
        return redirect(url)
    else:
        # In production, send the the `X-Accel-Redirect` and other headers
        # so that Nginx will reverse proxy
        response = HttpResponse()
        response["X-Accel-Redirect"] = "@account-content"
        response["X-Accel-Redirect-URL"] = url
        return response


def snapshot_index_html(
    request: HttpRequest, account: Account, project: Project, snapshot: Snapshot
) -> HttpResponse:
    """
    Return a snapshot's index.html.

    Adds necessary headers and injects content
    required to connect to a session.
    """
    if isinstance(snapshot.STORAGE, FileSystemStorage):
        # Serve the file from the filesystem.
        # Normally this will only be used during development!
        location = snapshot.file_location("index.html")
        with snapshot.STORAGE.open(location) as file:
            html = file.read()
    else:
        # Fetch the file from storage and send it on to the client
        url = snapshot.file_url("index.html")
        html = storage_client.get(url).content

    if not html:
        raise RuntimeError("No content")

    # Inject execution toolbar
    source_url = primary_domain_url(
        request,
        name="ui-projects-snapshots-retrieve",
        kwargs=dict(
            account=account.name, project=project.name, snapshot=snapshot.number,
        ),
    )
    session_provider_url = primary_domain_url(
        request,
        name="api-projects-snapshots-session",
        kwargs=dict(project=project.id, snapshot=snapshot.number),
    )
    toolbar = """
        <stencila-executable-document-toolbar
            source-url="{source_url}"
            session-provider-url="{session_provider_url}"
        >
        </stencila-executable-document-toolbar>
    """.format(
        source_url=source_url, session_provider_url=session_provider_url
    )
    html = html.replace(
        b'data-itemscope="root">', b'data-itemscope="root">' + toolbar.encode()
    )

    response = HttpResponse(html)

    # Add headers if the account has `hosts` set
    hosts = account.hosts
    if hosts:
        # CSP `frame-ancestors` for modern browers
        response["Content-Security-Policy"] = "frame-ancestors 'self' {};".format(hosts)
        # `X-Frame-Options` for older browsers (only allows one value)
        host = hosts.split()[0]
        response["X-Frame-Options"] = "allow-from {}".format(host)
    else:
        response["Content-Security-Policy"] = "frame-ancestors 'self';"
        response["X-Frame-Options"] = "sameorigin"

    return response


def primary_domain_url(request, name, kwargs):
    """
    Get a URL at the primary domain.

    See also the template tag by the same name.
    """
    protocol = "https" if request.is_secure() else "http"
    return protocol + "://" + settings.PRIMARY_DOMAIN + reverse(name, kwargs=kwargs)
