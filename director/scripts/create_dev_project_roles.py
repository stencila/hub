"""
Assign roles to the test users (if any exist in the db).
"""

import random
from django.contrib.auth.models import User
from projects.models import Project
from django.conf import settings


def random_role():
    roles = ['viewer', 'reader', 'reviewer', 'editor', 'manager', 'owner' ]
    return random.choice(roles)

def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    users = User.objects.all()
    projects = Project.objects.all()

    for user in users:
        for project in projects:
           UserProjectRole.user = user
           UserProjectRole.project = project
           UserProjectRole.role = random_role()
           UserProjectRole.save()
