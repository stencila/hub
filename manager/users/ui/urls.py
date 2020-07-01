from django.urls import include, path, re_path

from users.ui.views import (
    AcceptInviteView,
    SigninView,
    SignoutView,
    SignupView,
    redirect,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="ui-users-signup"),
    path("signin/", SigninView.as_view(), name="ui-users-signin"),
    path("signout/", SignoutView.as_view(), name="ui-users-signout"),
    path(
        "invites/accept/<str:key>",
        AcceptInviteView.as_view(),
        name="ui-users-invites-accept",
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
