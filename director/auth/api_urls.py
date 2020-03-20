from django.urls import re_path

from auth.api_views import GrantView, VerifyView, RefreshView, RevokeView

urlpatterns = [
    re_path(r"grant/?", GrantView.as_view(), name="api_auth_grant"),
    re_path(r"verify/?", VerifyView.as_view(), name="api_auth_verify"),
    re_path(r"refresh/?", RefreshView.as_view(), name="api_auth_refresh"),
    re_path(r"revoke/?", RevokeView.as_view(), name="api_auth_revoke"),
]
