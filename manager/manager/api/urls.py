"""
Module for defining all API URLs.

This needs to be a module separate from `../urls.py` so that it can be referred to
in `manager/api/views/docs.py` as the module from which the API schema is
generated.
"""
from django.urls import include, path, re_path

import accounts.api.urls
import jobs.api.urls
import projects.api.urls
import users.api.urls
from manager.api.views.docs import schema_view, swagger_view
from manager.api.views.status import StatusView

urlpatterns = (
    accounts.api.urls.urlpatterns
    + projects.api.urls.urlpatterns
    + jobs.api.urls.urlpatterns
    + users.api.urls.urlpatterns
    + [
        re_path(r"status/?", StatusView.as_view(), name="api-status"),
        path("", include("django_prometheus.urls")),
        re_path(r"schema/?", schema_view, name="api-schema"),
        # To avoid a `drf-yasg` warning, the following URL should end with a $
        re_path(r"^$|docs/$", swagger_view, name="api-docs"),
    ]
)
