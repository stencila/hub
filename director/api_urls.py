from django.urls import path, include
from users.api_v1_urls import urlpatterns as user_v1_patterns

urlpatterns = [
    path('v1/', include([
        path('users/', include(user_v1_patterns))
    ]))
]
