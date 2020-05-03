"""
Module for defining all API URLs.

This needs to be a module separate from `urls.py` so that it can be referred to
in `general/api/views/docs.py` as the module from which the API schema is
generated.
"""

import general.api.urls
import jobs.api.urls
import projects.api.urls
import users.api.urls

urlpatterns = (
    general.api.urls.urlpatterns
    + jobs.api.urls.urlpatterns
    + projects.api.urls.projects_urls
    + projects.api.urls.nodes.urls
    + users.api.urls.tokens.urls
    + users.api.urls.users.urls
)
