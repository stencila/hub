from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from users.models import User


class UsernameOrEmailBackend(ModelBackend):
    """
    Allows a user to authenticate using their usename or email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Override that checks for matching username and emails."""
        try:
            user = User.objects.filter(
                Q(username=username)
                | Q(email=username)
                | Q(emailaddress__email=username)
            )[0]
        except IndexError:
            return None
        else:
            if user.check_password(password):
                return user
        return None
