from django.urls import path, re_path
from rest_framework import routers

from general.api.views.docs import schema_view, swagger_view
from general.api.views.status import StatusView
from general.api.views.tokens import TokensViewSet

tokens = routers.SimpleRouter()
tokens.register(r"tokens", TokensViewSet, "api-tokens")

urlpatterns = [
    # API schema and docs
    path("schema/", schema_view, name="api-schema"),
    path("docs/", swagger_view, name="api-docs"),
    # System status
    re_path(r"status/?", StatusView.as_view(), name="api-status"),
] + tokens.urls
