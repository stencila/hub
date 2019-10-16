from polymorphic.models import PolymorphicModel

from lib.jwt import jwt_encode


class Host(PolymorphicModel):
    """An execution host."""

    @staticmethod
    def create(host_type):
        """Create a new editor of the given type."""
        if host_type == 'native':
            return NativeHost.objects.create()
        raise RuntimeError('Unhandled type "{}" when attempting to create host'.format(host_type))


class NativeHost(Host):
    """Stencila's native execution host based on stencila/cloud."""

    base_url = None

    def url(self):
        """Get the URL for this host session."""
        return self.base_url

    def token(self):
        """Get a JWT token for this host session."""
        return jwt_encode()  # payload will be empty except for iat
