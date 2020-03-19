from django.urls import path
from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    verify_jwt_token,
)

from auth.api_views import OpenIdGrantView

urlpatterns = [
    path("token/grant/", obtain_jwt_token, name="api_token_grant"),
    path("token/refresh/", refresh_jwt_token, name="api_token_refresh"),
    path("token/verify/", verify_jwt_token, name="api_token_verify"),
    path("openid/grant/", OpenIdGrantView.as_view(), name="api_openid_grant"),
]
