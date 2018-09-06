"""
Assign roles to the test users (if any exist in the db).
"""

import random
from django.contrib.auth.models import User
from projects.models import Project, UserProjectRole, ProjectPermission, ProjectRole
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    users = User.objects.all()
    projects = Project.objects.all()
    user_type = ContentType.objects.get(app_label='auth', model='user')

    for user in users:
        for project in projects:
          UserProjectRole.objects.create(
           user = user,
           agent_id = user.pk,
           content_type = user_type,
           project = project,
           role = ProjectRole.objects.order_by('?').first()
           )
