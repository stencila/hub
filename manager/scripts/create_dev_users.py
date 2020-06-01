from django.conf import settings
from django.contrib.auth.models import User


def run(*args):
    """Create users for the development database."""
    # Ensure that this is only used in development
    assert settings.DEBUG

    # Admin (super user)
    admin = User.objects.create_user(
        username="admin",
        password="admin",
        first_name="Admin",
        email="admin@example.com",
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    # Staff member (not super user)
    staff = User.objects.create_user(
        username="staff",
        password="staff",
        first_name="Staff",
        email="staff@example.com",
    )
    staff.is_staff = True
    staff.save()

    # Normal users
    user = User.objects.create_user(
        username="user", password="user", first_name="User", email="user@example.com",
    )
    user.save()

    for user in [
        ("joe", "Joe", "Blogs"),
        ("jane", "Jane", "Doe"),
        ("mike", "Mike", "Morris"),
        ("mary", "Mary", "Jones"),
    ]:
        User.objects.create_user(
            username=user[0],
            password=user[0],
            first_name=user[1],
            last_name=user[2],
            email=user[0] + "@example.com",
        )
