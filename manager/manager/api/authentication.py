import base64
import binascii

from django.conf import settings
from knox.auth import TokenAuthentication
from rest_framework.authentication import HTTP_HEADER_ENCODING, BaseAuthentication
from rest_framework.authentication import BasicAuthentication as DRFBasicAuthentication
from rest_framework.authentication import (
    SessionAuthentication,
    get_authorization_header,
)
from rest_framework.exceptions import AuthenticationFailed


class BasicAuthentication(BaseAuthentication):
    """
    HTTP Basic authentication allowing token as username.

    This class is based on `rest_framework.authentication.BasicAuthentication` but
    expects the username part of the header to be the `knox` token. This allows
    for easier use of `curl` and `httpie` for testing the API. e.g

        curl https://hub.stenci.la/api/me -u c3ddcf8be55cd6baa66da51efb0e8cae24aeb9c7b66f4c2a291a18afe2c09d1f:

    The trailing colon prevents curl from asking for a password.
    Inspired by [Stripe's approach](https://stripe.com/docs/api/authentication).

    Basic authentication using username/password is usually not allowed in production
    since that may encourage API users to store username/password unsafely in client applications.
    However, it can be turned on during development by setting `settings.API_BASIC_AUTH = True`.
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
                base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).split(":")
            )
        except (TypeError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationFailed(
                "Invalid Basic authorization header. Credentials not correctly base64 encoded."
            )

        username, password = (
            auth_parts if len(auth_parts) >= 2 else (auth_parts[0], None)
        )
        if password:
            if settings.API_BASIC_AUTH:
                return DRFBasicAuthentication().authenticate_credentials(
                    username, password, request
                )
            else:
                raise AuthenticationFailed(
                    "Basic authorization with a password is not allowed; use an API token instead."
                )
        else:
            # Treat the username as a token; pass it on to `knox.TokenAuthentication`
            token = username.encode("utf-8")
            return TokenAuthentication().authenticate_credentials(token)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Django Session authentication without CSRF check.

    For some API views it may be necessary to disable the CSRF protection.
    This enables that, use it by adding this to the view:

       authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication, knox.auth.TokenAuthentication)

    """

    def enforce_csrf(self, request):
        """
        Do not enforce CSRF.
        """
        return  # To not perform the csrf check previously happening
