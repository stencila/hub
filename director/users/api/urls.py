from django.urls import path

from users.api.views import UserSearch

urlpatterns = [
    path('search', UserSearch.as_view())
]
