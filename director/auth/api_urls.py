from django.urls import path
from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    verify_jwt_token,
)

from auth.api_views import OpenIdAuthView

urlpatterns = [
    path("token/grant/", obtain_jwt_token),
    path("token/refresh/", refresh_jwt_token),
    path("token/verify/", verify_jwt_token),
    path("openid/grant/", OpenIdAuthView.as_view()),
]
