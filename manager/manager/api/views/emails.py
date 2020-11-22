import logging

from rest_framework import generics
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from manager.signals import email_received

logger = logging.getLogger(__name__)


class EmailsView(generics.GenericAPIView):
    """
    A view for receiving parsed email payloads.
    """

    permission_classes = []
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request: Request) -> Response:
        """
        Receive an email.

        Returns an empty response.
        """
        email = request.data
        logger.info(f"Email received from {email.get('from')} to {email.get('to')}")
        email_received.send_robust(sender=self.__class__, email=email)
        return Response()
