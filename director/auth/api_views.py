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
import knox.auth
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, ParseError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import generics

# Claims verified for OpenID JWTs issued by Google
GOOGLE_ISS = "https://accounts.google.com"
GOOGLE_AUDS = [
    # Stencila Google Docs addon
    "110435422451-kafa0mb5tt5c5nfqou4kussbnslfajbv.apps.googleusercontent.com"
]


class GrantSerializer(serializers.Serializer):

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

    class Meta:
        ref_name = None


class GrantView(generics.GenericAPIView):
    """
    Grant an authentication token.

    Receives a POST with either (a) user's username and password, or (b) an OpenID Connect JSON Web Token.
    Returns the `username`, and an `token` that can be used for authenticated API requests.
    Currently, only OpenID tokens issued by Google are accepted.
    """

    permission_classes = ()
    serializer_class = GrantSerializer

    def post(self, request: Request) -> Response:
        serializer = GrantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        openid = serializer.validated_data.get("openid")

        if username and password:
            user = authenticate(request, username=username, password=password)
        elif openid:
            user = self.authenticate_openid(request, openid)
        else:
            user = request.user

        if not user:
            raise AuthenticationFailed()
        elif not user.is_authenticated:
            raise NotAuthenticated()

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        response = knox.views.LoginView().post(request)
        token = response.data["token"]

        response = Response({"token": token, "username": str(user)})
        return response

    @staticmethod
    def authenticate_openid(request, token):
        """Authenticate user using an OpenID token."""
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
            username = GrantView.generate_username(email, given_name, family_name)
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


class TokenSerializer(serializers.Serializer):

    token = serializers.CharField(help_text="Authentication token")

    class Meta:
        ref_name = None


class VerifyView(generics.GenericAPIView):
    """
    Verify a authentication token.

    Receives a POST with a `token`.
    Returns the same token if it is valid, `"token": null` if not.
    """

    permission_classes = ()
    serializer_class = TokenSerializer

    def post(self, request: Request) -> Response:
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get("token")

        try:
            auth = knox.auth.TokenAuthentication()
            auth.authenticate_credentials(token.encode("utf-8"))
            return Response({"token": token})
        except AuthenticationFailed:
            return Response({"token": None})


class RefreshView(generics.GenericAPIView):
    """
    Refresh an authentication token.

    Receives a POST with a previously granted token.
    Returns the refreshed token (with new expiration).
    """

    permission_classes = ()
    serializer_class = TokenSerializer

    def post(self, request: Request) -> Response:
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get("token")

        # Just authenticating the token will refresh it; the same token
        # is returned.
        auth = knox.auth.TokenAuthentication()
        auth.authenticate_credentials(token.encode("utf-8"))
        return Response({"token": token})


class RevokeView(generics.GenericAPIView):
    """
    Revoke an authentication token.

    Receives a POST with a previously granted token.
    Returns `"token": null` if successful.
    """

    permission_classes = ()
    serializer_class = TokenSerializer

    def post(self, request: Request) -> Response:
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get("token")

        auth = knox.auth.TokenAuthentication()
        user, token_instance = auth.authenticate_credentials(token.encode("utf-8"))
        token_instance.delete()
        return Response({"token": None})
