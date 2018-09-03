"""
Create users for the development database
"""

from django.contrib.auth.models import User
from django.conf import settings


def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    admin = User.objects.create_user(
        username='admin',
        email='admin',
        password='admin'
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    for user in ['joe', 'jane', 'mike', 'mary']:
        User.objects.create_user(
            username=user,
            password=user,
            email=user+'@example.com',
        )
