from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from google.auth.transport import requests
from google.oauth2.id_token import verify_token
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

GOOGLE_ISS = "https://accounts.google.com"

class OpenIdAuthView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request: Request) -> Response:
        transport = requests.Request()

        try:
            token = verify_token(request.data["token"], transport)
        except ValueError:
            raise PermissionDenied("Invalid token or signature")

        if token["iss"] != GOOGLE_ISS:
            raise PermissionDenied("Invalid iss")

        if not token["email_verified"]:
            raise PermissionDenied("Email address has not been verified")

        email = token["email"]

        # TODO: create user as well here
        user = get_object_or_404(User, email=email)

        login(request, user)

        payload = jwt_payload_handler(user)

        return Response({"token": jwt_encode_handler(payload), "user": user})
