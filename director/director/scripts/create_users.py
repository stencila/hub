from django.contrib.auth.models import User
from django.conf import settings
import json
import os
import warnings


def run(*args):
    try:
        path = os.path.join(settings.SECRETS_DIR, 'director-users.json')
        with open(path) as file:
            users = json.loads(file.read())
    except Exception:
        warnings.warn('Warning, unable to find user data', RuntimeWarning)
        users = [{
            'username': 'dev',
            'email': 'dev',
            'password': 'dev'
        }]

    # Create users
    for data in users:
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        user.is_staff = data.get('is_staff', False)
        user.is_superuser = data.get('is_superuser', False)
        user.save()
