import os

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.defaults import page_not_found, permission_denied
from sentry_sdk import last_event_id

from manager.api.exceptions import AccountQuotaExceeded


def home(request: HttpRequest) -> HttpResponse:
    """
    Home page view.

    Served at /. Redirects to other urls depending on whether
    the user is authenticated or not.
    """
    # Send OK to Google's health checker which always hits "/"
    # despite settings to the contrary.
    # This is a known bug being tracked here:
    # https://github.com/kubernetes/ingress-gce/issues/42
    # https://github.com/ory/k8s/issues/113#issuecomment-596281449
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    if "GoogleHC" in user_agent:
        return HttpResponse("OK")

    # Redirect to secure version. This needs to be done here to
    # avoid sending a 302 to GoogleHC.
    if settings.SECURE_SSL_REDIRECT and not request.is_secure():
        return redirect("https://" + request.get_host() + "/")

    # Authenticated users get redirected to dashboard
    if request.user.is_authenticated:
        return redirect("ui-accounts-retrieve", request.user.username)

    # Unauthenticated users get redirected to the project listing page
    return redirect("ui-projects-list")


def favicon(request: HttpRequest) -> HttpResponse:
    """
    Redirect clients to static favicon.

    Some browsers make a request for /favicon.ico.
    This redirects them to the static PNG.
    """
    return redirect(
        os.path.join(settings.STATIC_URL, "img", "favicon.png"), permanent=True
    )


def robots(request: HttpRequest) -> HttpResponse:
    """
    Return a robots.txt response.

    Allows access to all public (unauthenticated) pages.
    In addition SEO benefits, having this avoids losts of
    404 log entries for missing `robots.txt`.
    """
    return HttpResponse("User-Agent: *\nDisallow:\n", content_type="text/plain")


def render_template(request: HttpRequest) -> HttpResponse:
    """
    Render an arbitrary template.

    This view allows testing of templates during development.
    You can use it to preview templates for pages e.g.

       http://localhost:8000/stencila/render?template=403.html

    Or, for partial templates by using the `wrap` parameter e.g.

       http://localhost:8000/stencila/render?wrap=users/_search.html
    """
    template = request.GET.get("template", "base.html")
    wrap = request.GET.get("wrap")
    context = dict(wrap=wrap) if wrap else {}
    return render(request, template, context)


def test_account_quota_exceeded(request: HttpRequest) -> HttpResponse:
    """
    Test raising an `AccountQuotaExceeded` exception.

    Allows testing of the capture and rendering of the exception.
    """
    raise AccountQuotaExceeded(
        {"quota": "You went over some quota. Please upgrade your plan."}
    )


def test_messages(request: HttpRequest) -> HttpResponse:
    """
    Test creating user messages.

    Allows testing of the rendering of messages by the
    base template.
    """
    messages.debug(request, "A debug message")
    messages.info(request, "An info message.")
    messages.success(request, "A success message.")
    messages.warning(request, "A warning message.")
    messages.error(request, "An error message.")
    return render(request, "base.html")


# Handler for 403 errors is Django's default
# which will render the 403.html template
handle403 = permission_denied


def test403(request: HttpRequest) -> HttpResponse:
    """
    Test raising a 403 error.

    This view allows testing of 403 error handling in production
    (ie. test that custom 403 page is displayed)
    """
    raise PermissionDenied("This is a test 403 error")


# Handler for 404 errors in Django's  default
# which will render the 404.html template
handle404 = page_not_found


def test404(request: HttpRequest) -> HttpResponse:
    """
    Test raising a 404 error.

    This view allows testing of 404 error handling in production
    (ie. test that custom 404 page is displayed)
    """
    raise Http404("This is a test 404 error")


def handle500(request, *args, **argv):
    """
    Handle a 500 error.

    Adds details to the rendering context to be used in Sentry
    user feedback form (see the 500.html).
    """
    context = {
        "sentry_event_id": last_event_id(),
    }
    if request.user.is_authenticated:
        context.update(
            {
                "user_name": "{} {}".format(
                    request.user.first_name, request.user.last_name
                ),
                "user_email": request.user.email,
            }
        )
    return render(request, "500.html", context, status=500)


@staff_member_required
def test500(request: HttpRequest) -> HttpResponse:
    """
    Test raising a 500 error.

    This view allows testing of 500 error handling in production (e.g that stack traces are
    being sent to Sentry). Can only be tested by staff.
    """
    raise RuntimeError("This is a test 500 error")
