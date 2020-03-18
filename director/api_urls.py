from django.urls import path, include

from api_auth_views import OpenIdAuthView
from users.api_v1_urls import urlpatterns as user_v1_patterns
from projects.api_v1_urls import urlpatterns as project_v1_patterns
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

auth_patterns = [
    path('token/grant/', obtain_jwt_token),
    path('token/refresh/', refresh_jwt_token),
    path('token/verify/', verify_jwt_token),
    path('openid/grant/', OpenIdAuthView.as_view())
]

urlpatterns = [
    path('v1/', include([
        path('auth/', include(auth_patterns)),
        path('users/', include(user_v1_patterns)),
        path('projects/', include(project_v1_patterns))
    ]))
]
