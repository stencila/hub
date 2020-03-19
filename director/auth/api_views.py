import time

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from google.auth.transport import requests
from google.oauth2 import id_token
import jwt
from rest_framework_jwt.views import VerifyJSONWebToken
from rest_framework_jwt.serializers import (
    jwt_payload_handler,
    jwt_decode_handler,
    jwt_encode_handler,
)
from rest_framework import serializers
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# JWT claims verified for OpenID JWTs issued by Google
GOOGLE_ISS = "https://accounts.google.com"
GOOGLE_AUDS = [
    "110435422451-kafa0mb5tt5c5nfqou4kussbnslfajbv.apps.googleusercontent.com"
]


class OpenIdTokenSerializer(serializers.Serializer):
    """
    Checks that a token is provided
    """

    token = serializers.CharField(required=True)


class OpenIdGrantView(APIView):
    """
    Grants an authentication JSON Web Token (JWT) based on a OpenID Connect JWT.

    Currently, only OpenID JWTs issued by Google are accepted.
    """

    authentication_classes = ()
    permission_classes = ()
    serializer_class = OpenIdTokenSerializer

    def post(self, request: Request) -> Response:
        serializer = OpenIdTokenSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data.get("token")
        else:
            return bad_request(serializer.errors)

        try:
            unverified_claims = jwt.decode(token, None, False)
        except Exception as exc:
            return bad_request("Bad token: {}".format(str(exc)))

        # Validates token following recommendations at
        # https://developers.google.com/identity/protocols/oauth2/openid-connect#validatinganidtoken
        # Does basic validation before pinging Google to do token verification

        exp = unverified_claims.get("exp")
        if exp and float(exp) < time.time():
            return bad_request("Token has expired")

        if unverified_claims.get("iss") != GOOGLE_ISS:
            return bad_request("Invalid token issuer")

        if unverified_claims.get("aud") not in GOOGLE_AUDS:
            return bad_request("Invalid token audience")

        transport = requests.Request()
        try:
            claims = id_token.verify_token(token, transport)
        except ValueError:
            return bad_request("Token could not be verified")

        if not claims.get("email_verified"):
            return bad_request("Email address has not been verified")

        email = claims.get("email")
        given_name = claims.get("given_name")
        family_name = claims.get("family_name")
        name = claims.get("name")
        if name is not None and given_name is None and family_name is None:
            given_name, family_name = name.split()[:1]
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            username = self.generate_username(email, given_name, family_name)
            user = User.objects.create_user(
                username, email=email, first_name=given_name, last_name=family_name
            )

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        token = jwt_encode_handler(jwt_payload_handler(user))
        return Response({"token": token, "username": str(user)})

    @staticmethod
    def generate_username(email, given_name, family_name) -> str:
        email_name = slugify(email.split("@")[0]) if email else None
        username = email_name
        trial = 1
        while (
            not username or User.objects.filter(username=username).count() > 0
        ) and trial < 1000:
            trial += 1
            if trial == 2 and given_name:
                username = slugify(given_name)
            if trial == 3 and given_name and family_name:
                username = slugify(given_name + " " + family_name)
            elif trial == 4 and email:
                username = slugify(email)
            elif trial > 5:
                base = slugify(email_name) if email_name else "user"
                username = "{}{}".format(base, trial - 5)
        return username


def bad_request(message: str) -> Response:
    return Response(message, status=status.HTTP_400_BAD_REQUEST)
