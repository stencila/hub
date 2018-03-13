from django.contrib.auth.models import User


def run(*args):
    user = User.objects.create_user(
        username='hub',
        email='hub@stenci.la',
        password='hub'
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()
