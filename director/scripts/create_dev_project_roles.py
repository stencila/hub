"""
Assign roles to the test users (if any exist in the db).
"""

import random
from django.contrib.auth.models import User
from projects.models import Project, UserProjectRole, ProjectPermission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


def random_role():
    roles = ['viewer', 'reader', 'reviewer', 'editor', 'manager', 'owner' ]

    r = random.choice(roles)
    if ProjectPermission.type == r:
      return ProjectPermission

def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    users = User.objects.all()
    projects = Project.objects.all()
    user_type = ContentType.objects.get(app_label='auth', model='user')

    ProjectPermission.objects.create()

    for user in users:
        for project in projects:
          UserProjectRole.objects.create(
           user = user,
           agent_id = user.pk,
           content_type = user_type,
           project = project,
           role = random_role(),
           role_id = 1
           )
