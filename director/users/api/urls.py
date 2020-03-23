from django.urls import re_path

from users.api.views import UserSearch

urlpatterns = [
    re_path(r"search/?", UserSearch.as_view())
]
