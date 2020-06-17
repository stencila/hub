"""
Define models used in this app.

This module only serves to provide some consistency across the
`users`, `accounts` , `projects` etc apps so that you can
`from users.models import Users`, just like you can for
`from projects.models import Projects` and instead of having to remember
to do the following.
"""

from django.contrib.auth import get_user_model

User = get_user_model()
