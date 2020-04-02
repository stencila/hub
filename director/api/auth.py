import base64
import binascii

from knox.auth import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import HTTP_HEADER_ENCODING, get_authorization_header


class BasicAuthentication(TokenAuthentication):
    """
    HTTP Basic authentication using token as username.

    This class is based on `rest_framework.authentication.BasicAuthentication` but
    expects the username part of the header to be the `knox` token. This allows
    for easier use of `curl` and `httpie` for testing the API. e.g

        curl https://hub.stenci.la/api/me -u c3ddcf8be55cd6baa66da51efb0e8cae24aeb9c7b66f4c2a291a18afe2c09d1f:

    The trailing colon prevents curl from asking for a password.
    Inspired by [Stripe's approach](https://stripe.com/docs/api/authentication).

    We do not allow plain Basic authentication since that may encourage
    API users to store username/password unsafely in client applications.
    """

    def authenticate(self, request):
        """
        Authenticate a request.

        Returns a `User` if a valid token hs been supplied
        using HTTP Basic authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b"basic":
            return None

        if len(auth) == 1:
            raise AuthenticationFailed(
                "Invalid Basic authorization header. No credentials provided."
            )
        elif len(auth) > 2:
            raise AuthenticationFailed(
                "Invalid Basic authorization header. Credentials string should not contain spaces."
            )

        try:
            auth_parts = (
                base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(":")
            )
        except (TypeError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationFailed(
                "Invalid Basic authorization header. Credentials not correctly base64 encoded."
            )

        # Pass token on to `knox.TokenAuthentication`; ignore any password supplied
        token = auth_parts[0]
        return self.authenticate_credentials(token.encode("utf-8"))
