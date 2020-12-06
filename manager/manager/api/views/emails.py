import logging

from rest_framework import generics, serializers
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from manager.signals import email_received

logger = logging.getLogger(__name__)


class EmailSerializer(serializers.Serializer):
    """
    A serializer for emails.

    This serializer is mainly for documentation and is based on the fields
    sent by SendGrid. Note that Sendrid send `from` and `to` instead of
    `sender` and `recipient`.

    See https://sendgrid.com/docs/for-developers/parsing-email/setting-up-the-inbound-parse-webhook/#default-parameters
    """

    sender = serializers.CharField(
        help_text="Email sender, as taken from the message headers."
    )

    recipient = serializers.CharField(
        help_text="Email recipient field, as taken from the message headers."
    )

    subject = serializers.CharField(help_text="Email subject.")

    text = serializers.CharField(help_text="Email body in plaintext formatting.")

    html = serializers.CharField(
        help_text="HTML body of email. If not set, email did not have an HTML body."
    )

    spf = serializers.CharField(
        help_text="The results of the Sender Policy Framework verification of the message sender and receiving IP address."  # noqa
    )


class EmailsView(generics.GenericAPIView):
    """
    A view for receiving parsed email payloads.
    """

    permission_classes = []
    parser_classes = [MultiPartParser, JSONParser]
    serializer_class = EmailSerializer

    def post(self, request: Request) -> Response:
        """
        Receive an email.

        Returns an empty response.
        """
        email = request.data
        logger.info(f"Email received from {email.get('from')} to {email.get('to')}")
        email_received.send_robust(sender=self.__class__, email=email)
        return Response()
