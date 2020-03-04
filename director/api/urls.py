from django.urls import path, include, re_path
from rest_framework import routers

from api.views_docs import schema_view, swagger_view
from api.views_status import StatusView
from api.views_tokens import TokensViewSet
from projects.api.urls import urlpatterns as projects_urls
from projects.api.views_execution import RpcTransactionView
from users.api.urls import urlpatterns as users_urls

router = routers.SimpleRouter()
router.register(r"tokens", TokensViewSet, "api-tokens")

urlpatterns = [
    # System status
    re_path(r"status/?", StatusView.as_view(), name="api-status"),
    # API schema and docs
    path("schema/", schema_view, name="api-schema"),
    path("docs/", swagger_view, name="api-docs"),
    # API URLs for each app
    path("projects/", include(projects_urls)),
    path("users/", include(users_urls)),
    path('rpc-transactions/', RpcTransactionView.as_view())
] + router.urls
