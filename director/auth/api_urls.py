from django.urls import path

from auth.api_views import ObtainView, RefreshView, VerifyView, OpenIdView

urlpatterns = [
    path("obtain/", ObtainView.as_view(), name="api_auth_obtain"),
    path("refresh/", RefreshView.as_view(), name="api_auth_refresh"),
    path("verify/", VerifyView.as_view(), name="api_auth_verify"),
    path("openid/", OpenIdView.as_view(), name="api_auth_openid"),
]
