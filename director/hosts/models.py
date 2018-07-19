import time

from django.conf import settings
from django.db import models
import jwt
from polymorphic.models import PolymorphicModel


class Host(PolymorphicModel):
    """
    An execution host
    """

    @staticmethod
    def create(type):
        """
        Create a new editor of the given type
        """
        if type == 'native':
            return NativeHost.objects.create()
        else:
            raise RuntimeError('Unhandled type "{}" when attempting to create host'.format(type))


class NativeHost(Host):
    """
    Stencila's native execution host based on stencila/cloud.
    """

    base_url = settings.NATIVE_HOST_URL

    def url(self):
        """
        Get the URL for this host session
        """
        return self.base_url

    def token(self):
        """
        Get a JWT token for this host session
        """
        payload = dict(iat=time.time())
        return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode("utf-8")
