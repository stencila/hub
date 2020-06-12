from django.urls import include, path, re_path

from users.ui.views import SigninView, SignoutView, SignupView, redirect

urlpatterns = [
    path("signup/", SignupView.as_view(), name="ui-users-signup"),
    path("signin/", SigninView.as_view(), name="ui-users-signin"),
    path("signout/", SignoutView.as_view(), name="ui-users-signout"),
    path("", include("allauth.urls")),
    re_path(r"(?P<rest>.*)", redirect),
]
