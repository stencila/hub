from django.urls import path, include
from users.api_v1_urls import urlpatterns as user_v1_patterns
from projects.api_v1_urls import urlpatterns as project_v1_patterns
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    path('v1/', include([
        path('grant-token/', obtain_jwt_token),
        path('refresh-token/', refresh_jwt_token),
        path('users/', include(user_v1_patterns)),
        path('projects/', include(project_v1_patterns))
    ]))
]
