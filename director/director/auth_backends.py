import random
import string

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db import IntegrityError

import logging
logger = logging.getLogger('authentication')

class GuestAuthBackend(ModelBackend):
    '''
    Creates a guest user. See `users.models.login_guest_user`
    '''

    def authenticate(self, stencila_guest_auth, **kwargs):
        user = None
        trials = 0
        while trials < 100:
            trials += 1
            username = 'guest-'+''.join(random.sample(string.digits, 6))
            try:
                user = User.objects.create_user(
                    username=username,
                    # Use email as a signal to `user_post_save` that this is a guest
                    email="guest"
                )
                break
            except IntegrityError:
                if trials >= 30:
                    logger.error('Needing many trials at generating a random auto user username. Increase digits?')

        if user is None:
            raise Exception('Unable to create GuestAuthBackend user')
        else:
            return user
