from django.db import models
from jsonfallback.fields import FallbackJSONField


class RpcTransaction(models.Model):
    request_host = models.TextField(blank=False,
                                    null=False,
                                    help_text='The host that generated the request. May be a FQDN or simple '
                                              'identifying string.')
    response_host = models.TextField(blank=True,
                                     null=True,
                                     help_text='THe host that response to the request (generated the response). May be '
                                               'a FQDN or simple identifying string, or null if the Transaction has'
                                               'no response (e.g. it\'s a notification).')
    transaction_id = models.TextField(blank=True,
                                      null=True,
                                      help_text='The transaction ID, used to link together the request and response.'
                                                'Should be unique for the request_host. Will be null for notification '
                                                'requests.')

    method = models.TextField(blank=True,
                              null=True,
                              help_text='The JSON RPC method (from the request).')

    params = FallbackJSONField(blank=True,
                               null=True,
                               help_text='The JSON RPC params (from the request).')

    result = FallbackJSONField(blank=True,
                               null=True,
                               help_text='The JSON RPC result (from the response).')

    error = FallbackJSONField(blank=True,
                              null=True,
                              help_text='The JSON RPC error (from the response). Usually null.')

    request_time = models.DateTimeField(blank=True,
                                        null=True,
                                        help_text='The date/time the request to record the request was received.')

    response_time = models.DateTimeField(blank=True,
                                         null=True,
                                         help_text='The date/time the request to record the response was received.')

    transport = models.TextField(blank=False, null=False, help_text='The transport over which the transaction was '
                                                                    'communicated. E.g. ws, tcp:3000, https:443, etc.')

    class Meta:
        unique_together = (('request_host', 'transaction_id'),)
