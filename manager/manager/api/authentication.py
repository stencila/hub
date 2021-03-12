import base64
import binascii
import logging

from django.conf import settings
from knox.auth import TokenAuthentication
from rest_framework.authentication import HTTP_HEADER_ENCODING, BaseAuthentication
from rest_framework.authentication import BasicAuthentication as DRFBasicAuthentication
from rest_framework.authentication import (
    SessionAuthentication,
    get_authorization_header,
)
from rest_framework.exceptions import AuthenticationFailed

from users.socialaccount.tokens import refresh_user_access_token

logger = logging.getLogger(__name__)


class BasicAuthentication(BaseAuthentication):
    """
    HTTP Basic authentication allowing a token as username.

    This class is based on `rest_framework.authentication.BasicAuthentication` but
    expects the username part of the header to be the `knox` token. This allows
    for easier use of `curl` and `httpie` with the API. e.g

        curl https://hub.stenci.la/api/users/me -u c3ddcf8be55cd6baa66da51efb0e8cae24aeb9c7b66f4c2a291a18afe2c09d1f:

    The trailing colon prevents curl from asking for a password.
    Inspired by [Stripe's approach](https://stripe.com/docs/api/authentication).

    Basic authentication using username/password is usually not allowed in production
    since that may encourage API users to store username/password unsafely in client applications.
    However, it can be turned on during development by setting `settings.API_BASIC_AUTH = True`.
    """

    def authenticate(self, request):
        """
        Authenticate a request.

        Returns a `User` if a valid token has been supplied
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


class RefreshOAuthTokenAuthentication(BaseAuthentication):
    """
    Authentication that allows for adding / updating a `SocialToken` for a `SocialApp`.

    Most of the time users will take the normal `allauth` based flow to authenticate
    using a third-party provider e.g. Google. In these cases, we store a
    access token to use for that provider on behalf of the user (and usually a
    refresh token).

    However, in other cases, such as a client using the Hub's API, the user may
    NOT yet have gone through this flow but we still want to be able to pass along
    an access token for a for a `SocialApp` (e.g. for pulling a source from that provider).

    Pass the access token in the `OAuth-Token` header with the name of the social app e.g.

        OAuth-Token: gas fk52.RbLsRS3uO0TkPOchy22...

    This header name was chosen as it does not clash with any of those registered
    (https://www.iana.org/assignments/message-headers/message-headers.xhtml) and
    the `X-` prefix for custom headers is deprecated.

    This would ideally be middleware (it's not an authenticator) but DRF does
    not support that and this seems to be the best alternative.
    See https://github.com/encode/django-rest-framework/issues/7607
    """

    def authenticate(self, request):
        """
        Implement authenticator interface.

        See https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication
        """
        # Try to authenticate with the "real" authenticators
        user_auth = BasicAuthentication().authenticate(request)
        if not user_auth:
            user_auth = TokenAuthentication().authenticate(request)

        # Not authenticated so leave
        if not user_auth:
            return None

        # Authenticated, so look for special header...
        # This is wrapped in a try/catch because we really don't want
        # this side-effect to stop the authentication process
        try:
            user, auth = user_auth
            header = request.META.get("HTTP_OAUTH_TOKEN")
            if header:
                parts = header.split(" ")
                if len(parts) == 2:
                    social_app, token = parts
                    refresh_user_access_token(user, social_app, token)
        except Exception:
            logger.error("Error attempting to refresh OAuth token", exc_info=True)

        return user_auth


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
