from hmac import compare_digest
import binascii
import time
import typing

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import serializers
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    ParseError,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework import viewsets
import jwt
import knox.auth
import knox.models
import knox.views
import knox.crypto
from knox.settings import CONSTANTS as KNOX_CONSTANTS, knox_settings

from .serializers import TokenSerializer


# Claims verified for OpenID JWTs issued by Google
GOOGLE_ISS = "https://accounts.google.com"
GOOGLE_AUDS = [
    # Stencila Google Docs addon
    "110435422451-kafa0mb5tt5c5nfqou4kussbnslfajbv.apps.googleusercontent.com"
]


class TokensCreateRequest(serializers.Serializer):
    """The request data when creating a new token."""

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


class TokensCreateResponse(TokenSerializer):
    """The response data when creating a new token."""

    token = serializers.CharField(help_text="Authentication token string.")

    user = serializers.IntegerField(
        help_text="The id of the user that was authenticated."
    )

    username = serializers.CharField(
        help_text="The username of the user that was authenticated."
    )

    first_name = serializers.CharField(
        help_text="The first name of the user that was authenticated."
    )

    last_name = serializers.CharField(
        help_text="The last name of the user that was authenticated."
    )

    class Meta:
        model = TokenSerializer.Meta.model
        fields = TokenSerializer.Meta.fields + [
            "token",
            "user",
            "username",
            "first_name",
            "last_name",
        ]
        ref_name = None


class TokensViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = TokenSerializer
    lookup_url_kwarg = "token"

    def get_queryset(self):
        """
        Get the query set for these views.

        Returns all tokens currently associated with the user, including
        any that may be expired.
        """
        user = self.request.user
        return user.auth_token_set.all()

    def get_object(self, token=None):
        """
        Get and refresh an authentication token instance.

        For security reasons the database does not hold the actual tokens,
        so it is necessary to iterate through those tokens with a matching
        `token_key` (the first eight characters).

        This is based on `knox.auth.TokenAuthentication.authenticate_credentials()`
        but does not cleanup expired tokens and raises `NotFound` instead
        of `AuthenticationFailed`.
        """
        if token is None:
            token = self.kwargs["token"]

        for auth_token in knox.models.AuthToken.objects.filter(
            token_key=token[: KNOX_CONSTANTS.TOKEN_KEY_LENGTH],
            expiry__gt=timezone.now(),
        ):
            try:
                digest = knox.crypto.hash_token(token, auth_token.salt)
            except (TypeError, binascii.Error):
                raise NotFound()

            if compare_digest(digest, auth_token.digest):
                if knox_settings.AUTO_REFRESH and auth_token.expiry:
                    knox.auth.TokenAuthentication.renew_token(None, auth_token)
                return auth_token
        raise NotFound()

    def get_permissions(self):
        """
        Get the list of permissions that the current action requires.

        Listing token needs the user to be authenticated, but `create`
        (credentials are POSTed in the request body), `retrieve` and `destroy` do not
        (token is a parameter in the request URL).
        """
        if self.action == "list":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def list(self, request):
        """
        List authentication tokens.

        Returns a list of the authentication tokens for the current user.
        Stencila does not store the raw token only the `id` (the first eight characters).
        """
        return super().list(request)

    @swagger_auto_schema(
        request_body=TokensCreateRequest,
        responses={HTTP_201_CREATED: TokensCreateResponse},
    )
    def create(self, request: Request) -> Response:
        """
        Create an authentication token.

        Receives a POST with either (a) user's username and password, or (b) an OpenID Connect JSON Web Token.
        Returns the `username`, and an `token` that can be used for authenticated API requests.
        Currently, only OpenID tokens issued by Google are accepted.
        """
        serializer = TokensCreateRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        openid = serializer.validated_data.get("openid")

        if username and password:
            user = authenticate(request, username=username, password=password)
        elif openid:
            user = authenticate_openid(request, openid)
        else:
            user = request.user

        if not user:
            raise AuthenticationFailed()
        elif not user.is_authenticated:
            raise NotAuthenticated()

        request.user = user
        response = knox.views.LoginView().post(request)
        token = response.data["token"]
        auth_token = self.get_object(token)

        return Response(
            {
                "token": token,
                "id": auth_token.token_key,
                "created": auth_token.created,
                "expiry": auth_token.expiry,
                "user": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            status=HTTP_201_CREATED,
        )

    def retrieve(self, request: Request, token=None) -> Response:
        """
        Retrieve and refresh an authentication token.

        Returns details of the authentication token identified including
        it's new expiry date.
        """
        return super().retrieve(request, token)

    def destroy(self, request: Request, token=None) -> Response:
        """
        Destroy an authentication token.

        Deletes the token, whether or not is is expired.
        """
        return super().destroy(request, token)


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
        username = generate_username(email, given_name, family_name)
        user = User.objects.create_user(
            username, email=email, first_name=given_name, last_name=family_name
        )

    return user


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
