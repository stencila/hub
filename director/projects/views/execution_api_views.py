from django.http import HttpRequest
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from projects.api_serializers import RpcTransactionSerializer
from projects.execution_models import RpcTransaction


class RpcTransactionView(generics.ListAPIView):
    queryset = RpcTransaction.objects.all()
    serializer_class = RpcTransactionSerializer
    permission_classes = [IsAdminUser]

    def post(self, request: HttpRequest) -> dict:
        # Since a transaction is a request + response, and we don't know which this one is, call it a half transaction
        half_transaction = request.data

        if not half_transaction.get('request_host'):
            raise ValueError('Unable to store a transaction without a request_host value.')

        payload = half_transaction['payload']

        defaults = {
            'transport': half_transaction['transport'],
            'method': payload.get('method'),
            'params': payload.get('params'),
            'result': payload.get('result'),
            'error': payload.get('error')
        }

        if 'method' in payload and ('result' in payload or 'error' in payload):
            raise ValueError('Payload contains both method and result/error, can not determine its type.')

        if 'method' in payload:
            defaults['request_time'] = timezone.now()
            is_request = True
        elif 'result' in payload or 'error' in payload:
            defaults['response_time'] = timezone.now()
            is_request = False
        else:
            raise TypeError('Unable to determine request or response from payload.')

        if payload.get('id'):
            transaction, created = RpcTransaction.objects.get_or_create(transaction_id=payload.get('id'),
                                                                        request_host=half_transaction['request_host'],
                                                                        defaults=defaults)

            if not created:
                # make sure we're not setting values twice
                if is_request:
                    if transaction.request_time:
                        raise ValueError('Request already recorded for transaction')
                    transaction.request_time = timezone.now()
                    transaction.method = payload.get('method')
                    transaction.params = payload.get('params')
                else:
                    if transaction.response_time:
                        raise ValueError('Response already recorded for transaction')
                    transaction.response_host = half_transaction['response_host']
                    transaction.response_time = timezone.now()
                    transaction.result = payload.get('result')
                    transaction.error = payload.get('error')

                transaction.save()
        else:
            if 'method' not in payload:
                raise ValueError('Attempting to log a notification without a method.')
            # this is a notification, so don't try to update an existing one
            transaction = RpcTransaction.objects.create(request_host=half_transaction['request_host'],
                                                        transport=half_transaction['transport'],
                                                        method=payload['method'],
                                                        params=payload.get('params'),
                                                        request_time=timezone.now()
                                                        )

        return {'success': True, 'transaction_pk': transaction.pk}
