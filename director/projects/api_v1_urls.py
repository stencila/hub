from django.urls import path

from .api_views import (
    ProjectRetrieveAPIView,
    ProjectSourceListAPIView,
    ProjectSourceRetrieveDestroyAPIView,
    ProjectFileSourceCreateAPIView
)

urlpatterns = [
    path('<int:pk>', ProjectRetrieveAPIView.as_view()),
    path('<int:pk>/sources', ProjectSourceListAPIView.as_view()),
    path('<int:pk>/sources/<int:source>', ProjectSourceRetrieveDestroyAPIView.as_view()),
    path('<int:pk>/sources/file', ProjectFileSourceCreateAPIView.as_view())
]
