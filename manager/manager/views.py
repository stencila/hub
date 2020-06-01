import os

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.defaults import page_not_found, permission_denied
from sentry_sdk import last_event_id


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
        return redirect("dashboard")

    # Unauthenticated users get redirected to sign in
    return redirect(settings.LOGIN_URL)


def favicon(request: HttpRequest) -> HttpResponse:
    """
    Redirect clients to static favicon.

    Some browsers make a request for /favicon.ico.
    This redirects them to the static PNG.
    """
    return redirect(
        os.path.join(settings.STATIC_URL, "img", "favicon.png"), permanent=True
    )


# Handler for 403 errors is Django's default
# which will render the 403.html template
handle403 = permission_denied


def test403(request: HttpRequest) -> HttpResponse:
    """
    A 403 view to test a 403 error.

    This view allows testing of 403 error handling in production
    (ie. test that custom 403 page is displayed)
    """
    raise PermissionDenied("This is a test 403 error")


# Handler for 404 errors in Django's  default
# which will render the 404.html template
handle404 = page_not_found


def test404(request: HttpRequest) -> HttpResponse:
    """
    A 404 view to test a 404 error.

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
    A 500 view to test a 500 error.

    This view allows testing of 500 error handling in production (e.g that stack traces are
    being sent to Sentry). Can only be tested by staff.
    """
    raise RuntimeError("This is a test 500 error")
