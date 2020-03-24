from django.urls import path, include, re_path
from django.views.generic import TemplateView

from auth.api.urls import urlpatterns as auth_urls
from projects.api.urls import urlpatterns as project_urls
from users.api.urls import urlpatterns as user_urls

from api.views import schema_view, StatusView

urlpatterns = [
    # System status
    re_path(r"status/?", StatusView.as_view(), name="api_status"),

    # API schema and docs
    path("schema/", schema_view, name="api_schema"),
    path(
        "docs/", TemplateView.as_view(template_name="api_swagger.html"), name="api_docs"
    ),

    # API URLs for each app
    path("auth/", include(auth_urls)),
    path("projects/", include(project_urls)),
    path("users/", include(user_urls)),
]
