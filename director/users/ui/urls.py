from django.urls import path, include

import users.ui.views as views

urlpatterns = [
    path("", views.UserSettingsView.as_view(), name="user_settings"),
    path("signup/", views.UserSignupView.as_view(), name="user_signup"),
    path("signin/", views.UserSigninView.as_view(), name="user_signin"),
    path("signout/", views.UserSignoutView.as_view(), name="user_signout"),
    path("dashboard/", views.UserDashboardView.as_view(), name="ui-user-dashboard"),
    path("username/", views.UsernameChangeView.as_view(), name="user_change_username"),
    path("avatar/", include("avatar.urls")),
    path("", include("allauth.urls")),
]
