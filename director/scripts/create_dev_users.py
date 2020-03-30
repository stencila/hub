"""Create users for the development database."""

from django.contrib.auth.models import User
from django.conf import settings


def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    # Admin (super user)
    admin = User.objects.create_user(
        username='admin',
        first_name='Admin',
        email='admin@example.com',
        password='admin'
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    # Staff member (not super user)
    staff = User.objects.create_user(
        username='staff',
        first_name='Staff',
        email='staff@example.com',
        password='staff'
    )
    staff.is_staff = True
    staff.save()

    # Normal users
    for user in [
        ('joe', 'Joe', 'Blogs'),
        ('jane', 'Jane', 'Doe'),
        ('mike', 'Mike', 'Morris'),
        ('mary', 'Mary', 'Jones')
    ]:
        User.objects.create_user(
            username=user[0],
            password=user[0],
            first_name=user[1],
            last_name=user[2],
            email=user[0]+'@example.com',
        )
