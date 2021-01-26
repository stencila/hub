from django.contrib.auth.decorators import login_required
from django.urls import include, path, re_path

from users.ui.views import (
    AcceptInviteView,
    ConnectionsView,
    EmailsView,
    PasswordChangeView,
    SigninView,
    SignoutView,
    SignupView,
    features,
    invites_create,
    invites_list,
    redirect,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="ui-users-signup"),
    path("signin/", SigninView.as_view(), name="ui-users-signin"),
    path("signout/", SignoutView.as_view(), name="ui-users-signout"),
    path(
        "invites/",
        include(
            [
                path("", invites_list, name="ui-users-invites-list",),
                path("send", invites_create, name="ui-users-invites-create",),
                path(
                    "accept/<str:key>",
                    AcceptInviteView.as_view(),
                    name="ui-users-invites-accept",
                ),
            ]
        ),
    ),
    path("features/", features, name="ui-users-features"),
    # Overrides of allauth URLs, conservatively retaining their path and names
    # See https://django-allauth.readthedocs.io/en/latest/views.html
    path(
        "password/change/",
        login_required(PasswordChangeView.as_view()),
        name="account_change_password",
    ),
    path("email/", login_required(EmailsView.as_view()), name="account_email"),
    path(
        "social/connections/",
        login_required(ConnectionsView.as_view()),
        name="socialaccount_connections",
    ),
    path("", include("allauth.urls")),
    # Redirect to the user's personal account
    # e.g. /me/settings -> username/settings
    #
    # Care needs to be taken to have a slash at the end of any
    # of the above URLs (including `invitations` or `allauth`)
    # otherwise they will get redirected also e.g
    # /me/send-invite/ : 200 OK
    # /me/send-invite -> username/send-invite/ : 404 Not Found
    re_path(r"(?P<rest>.*)", redirect),
]
