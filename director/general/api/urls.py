from django.urls import path, re_path

from general.api.views.docs import schema_view, swagger_view
from general.api.views.status import StatusView

urlpatterns = [
    # API schema and docs
    path("", swagger_view, name="api-docs"),
    re_path(r"schema/?", schema_view, name="api-schema"),
    # System status
    re_path(r"status/?", StatusView.as_view(), name="api-status"),
]
