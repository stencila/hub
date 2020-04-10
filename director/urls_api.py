"""
Module for defining all API URLs.

This needs to be a module sparate from `urls.py` so that it can be referrred to
in `general/api/views/docs.py` as the module from which the API schema is
generated.
"""

from django.urls import path, re_path, include

from general.api.urls import urlpatterns as api_general_urls
import projects.api.urls
import users.api.urls

urlpatterns = api_general_urls + [
    path("projects/", include(projects.api.urls.projects_urls)),
    path("nodes/", include(projects.api.urls.nodes_urls)),
    re_path("tokens/?", include(users.api.urls.tokens.urls)),
    re_path("users/?", include(users.api.urls.users.urls)),
]
