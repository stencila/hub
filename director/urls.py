from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.defaults import permission_denied, page_not_found
from django.shortcuts import render
from sentry_sdk import last_event_id

import views

# Specify sub paths as their own patterns to make it easier to see which root
# paths are defined in urlpatterns this will make it easier to keep the
# DISALLOWED_ACCOUNT_SLUGS up to date
from lib.constants import UrlRoot

about_urls = [
    path("", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("help/", views.HelpView.as_view(), name="help"),
]

test_urls = [
    path("403/", views.Test403View.as_view()),
    path("404/", views.Test404View.as_view()),
    path("500/", views.Test500View.as_view()),
]

urlpatterns = [
    # All in alphabetical order. Patterns that are fully defined in urlpatterns come first
    # Home page
    path("", views.HomeView.as_view(), name="home"),
    # ico for old browsers
    path(UrlRoot.favicon.value, views.IcoView.as_view()),
    # Redirect IE users to this view
    path(
        UrlRoot.ie_unsupported.value + "/",
        views.IeUnsupportedView.as_view(),
        name="ie-unsupported",
    ),
    # Patterns that include other urlpatterns or files
    # About pages etc
    path(UrlRoot.about.value + "/", include(about_urls)),
    # Accounts App
    path(UrlRoot.accounts.value + "/", include("accounts.urls")),
    # Staff (Django) admin
    path(UrlRoot.admin.value + "/", admin.site.urls),
    # API
    path(UrlRoot.api.value + "/", include("urls_api")),
    # User sign in, settings etc
    path(UrlRoot.me.value + "/", include("users.ui.urls")),
    # StencilaOpen App
    path(UrlRoot.open.value + "/", include("stencila_open.urls")),
    # Projects App
    path(UrlRoot.projects.value + "/", include("projects.urls")),
    # Testing errors
    path(UrlRoot.test.value + "/", include(test_urls)),
    # Custom Roots (they start with a slug)
    path("<slug:account_name>/", include("accounts.slug_urls")),
]

handler403 = permission_denied
handler404 = page_not_found


def handler500(request, *args, **argv):
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
    return render(request, "500.html", context, status=500,)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = (
        [path(UrlRoot.debug.value + "/", include(debug_toolbar.urls))]
        + urlpatterns
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
