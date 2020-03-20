import time
import typing

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from google.auth.transport import requests
from google.oauth2 import id_token
import jwt
import knox.views
from rest_framework_jwt.serializers import (
    jwt_payload_handler,
    jwt_encode_handler,
    RefreshJSONWebTokenSerializer,
    VerifyJSONWebTokenSerializer,
)
from rest_framework_jwt.views import (
    RefreshJSONWebToken,
    VerifyJSONWebToken,
)
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, ParseError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import generics

# JWT claims verified for OpenID JWTs issued by Google
GOOGLE_ISS = "https://accounts.google.com"
GOOGLE_AUDS = [
    "110435422451-kafa0mb5tt5c5nfqou4kussbnslfajbv.apps.googleusercontent.com"
]


class ObtainSerializer(serializers.Serializer):

    username = serializers.CharField(required=False, help_text="User's username")

    password = serializers.CharField(
        write_only=True,
        required=False,
        help_text="User's password",
        style={"input_type": "password", "placeholder": "Password"},
    )

    openid = serializers.CharField(
        write_only=True, required=False, help_text="An OpenID Connect JSON Web Token."
    )

    token_type = serializers.ChoiceField(
        ["uat", "jwt"],
        default="uat",
        help_text="The type of authentication token desired.",
    )

    class Meta:
        ref_name = None


class ObtainView(generics.GenericAPIView):
    """
    Obtain an authentication token.

    Receives a POST with either (a) user's username and password,
    or (b) an OpenID Connect JSON Web Token.
    Returns the username, token_type and a token that can be used for authenticated requests.
    Currently, only OpenID tokens issued by Google are accepted.
    """

    permission_classes = ()
    serializer_class = ObtainSerializer

    def post(self, request: Request) -> Response:
        serializer = ObtainSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")
            openid = serializer.validated_data.get("openid")
            token_type = serializer.validated_data.get("token_type")
        else:
            raise ParseError(serializer.errors)

        if username and password:
            user = authenticate(request, username=username, password=password)
        elif openid:
            user = self.login_openid(request, openid)
        else:
            user = request.user

        if not user:
            raise AuthenticationFailed()
        elif not user.is_authenticated:
            raise NotAuthenticated()

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        if token_type == "jwt":
            token = jwt_encode_handler(jwt_payload_handler(user))
        else:
            response = knox.views.LoginView().post(request)
            token = response.data["token"]

        return Response(
            {"token": token, "token_type": token_type, "username": str(user)}
        )

    @staticmethod
    def login_openid(request, token):
        """Login using an OpenID token."""
        try:
            unverified_claims = jwt.decode(token, None, False)
        except Exception as exc:
            raise ParseError("Bad token: {}".format(str(exc)))

        # Validates token following recommendations at
        # https://developers.google.com/identity/protocols/oauth2/openid-connect#validatinganidtoken
        # Does basic validation before pinging Google to do token verification

        exp = unverified_claims.get("exp")
        if exp and float(exp) < time.time():
            raise ParseError("Token has expired")

        if unverified_claims.get("iss") != GOOGLE_ISS:
            raise ParseError("Invalid token issuer")

        if unverified_claims.get("aud") not in GOOGLE_AUDS:
            raise ParseError("Invalid token audience")

        transport = requests.Request()
        try:
            claims = id_token.verify_token(token, transport)
        except ValueError:
            raise ParseError("Token could not be verified")

        if not claims.get("email_verified"):
            raise ParseError("Email address has not been verified")

        email = claims.get("email")
        given_name = claims.get("given_name")
        family_name = claims.get("family_name")
        name = claims.get("name")
        if name is not None and given_name is None and family_name is None:
            given_name, family_name = name.split()[:1]
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            username = ObtainView.generate_username(email, given_name, family_name)
            user = User.objects.create_user(
                username, email=email, first_name=given_name, last_name=family_name
            )

        return user

    @staticmethod
    def generate_username(
        email: typing.Optional[str],
        given_name: typing.Optional[str],
        family_name: typing.Optional[str],
    ) -> str:
        """
        Generate a username from an email address, given name and/or family name.

        See tests for examples.
        """

        def check_name(name):
            username = slugify(name)
            if name and User.objects.filter(username=username).count() == 0:
                return username
            else:
                return None

        email_name = check_name(email.split("@")[0]) if email else None
        if email_name:
            return email_name

        given_slug = check_name(given_name) if given_name else None
        if given_slug:
            return given_slug

        name_slug = (
            check_name(given_name + " " + family_name)
            if given_name and family_name
            else None
        )
        if name_slug:
            return name_slug

        email_slug = check_name(email) if email else None
        if email_slug:
            return email_slug

        base_name = email_name if email_name else "user"
        existing = User.objects.filter(username__startswith=base_name + "-").count()
        return "{}-{}".format(base_name, existing + 1)


# The following overrides of classes from `rest_framework_jwt`
# are just to customize their representation in the API schema.
# But in the future, more overrides could be done.
# The ref_name = None prevents the request data from being shown
# as a model.


class VerifySerializer(VerifyJSONWebTokenSerializer):
    class Meta:
        ref_name = None


class VerifyView(VerifyJSONWebToken):
    """
    Verify a JWT authentication token.

    Receives a POST with a token.
    Returns the same token if it is valid.
    """

    serializer_class = VerifySerializer


class RefreshSerializer(RefreshJSONWebTokenSerializer):
    class Meta:
        ref_name = None


class RefreshView(RefreshJSONWebToken):
    """
    Refresh a JWT  authentication token.

    Receives a POST with an previously obtained token.
    Returns a refreshed token (with new expiration) based on
    existing token.

    If 'orig_iat' field (original issued-at-time) is found, will first check
    if it's within expiration window, then copy it to the new token.
    """

    serializer_class = RefreshSerializer
