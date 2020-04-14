"""
Module for defining all API URLs.

This needs to be a module sparate from `urls.py` so that it can be referrred to
in `general/api/views/docs.py` as the module from which the API schema is
generated.
"""

from django.urls import re_path, include

from general.api.urls import urlpatterns as api_general_urls
import projects.api.urls
import users.api.urls

urlpatterns = api_general_urls + [
    re_path(r"projects/?", include(projects.api.urls.projects_urls)),
    re_path(r"nodes/?", include(projects.api.urls.nodes_urls)),
    re_path(r"tokens/?", include(users.api.urls.tokens.urls)),
    re_path(r"users/?", include(users.api.urls.users.urls)),
]
