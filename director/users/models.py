"""
Define models used in this app.

This module only serves to provide some consistency across the
`users`, `accounts` , `projects` etc apps so that you can
`from users.models import Users`, just like you can for
`from projects.models import Projects` and instead of having to remember
`from django.contrib.auth.models import User`.
"""

from django.contrib.auth.models import User  # noqa F401
