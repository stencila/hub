"""
Module for defining all API URLs.

This needs to be a module separate from `../urls.py` so that it can be referred to
in `manager/api/views/docs.py` as the module from which the API schema is
generated.
"""
from django.urls import re_path

from manager.api.views.docs import schema_view, swagger_view
from manager.api.views.status import StatusView
import users.api.urls

urlpatterns = [
    # API schema and docs
    re_path(r"^$|(docs/?)", swagger_view, name="api-docs"),
    re_path(r"^schema/?", schema_view, name="api-schema"),
    # System status
    re_path(r"^status/?", StatusView.as_view(), name="api-status")
 ] + users.api.urls.tokens.urls + users.api.urls.users.urls
