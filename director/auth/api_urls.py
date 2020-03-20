from django.urls import path

from auth.api_views import GrantView, VerifyView, RefreshView, RevokeView

urlpatterns = [
    path("grant", GrantView.as_view(), name="api_auth_grant"),
    path("verify", VerifyView.as_view(), name="api_auth_verify"),
    path("refresh", RefreshView.as_view(), name="api_auth_refresh"),
    path("revoke", RevokeView.as_view(), name="api_auth_revoke"),
]
