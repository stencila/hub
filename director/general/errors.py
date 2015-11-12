'''
Base `Error` exception class and  `ErrorMiddleware`
for raising and handling error exceptions
'''
from django.http import JsonResponse


class Error(Exception):
    '''
    Base exception class for custom exceptions.
    Override the `serialize()` method
    '''

    code = 500

    def serialize(self):
        return dict(
            error='general-error',
            message='An error occurred'
        )


class ErrorMiddleware(object):
    '''
    Converts an `Error` exception into a HTML or JSON depending
    on the request type
    '''

    def process_exception(self, request, exception):
        if isinstance(exception, Error):
            return JsonResponse(
                exception.serialize(),
                status=exception.code
            )
