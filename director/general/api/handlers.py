import traceback

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from sentry_sdk import capture_exception


def custom_exception_handler(exc, context):
    """
    Handle API exceptions.

    Produces response data with this structure:

        {
            "message" : "Invalid input.",
            "errors" : [
                {
                    "field" : "name",
                    "message" : "This field is required."
                }
            ]
        }

    The `message` string is always present but the `errors` array may not.

    Inspired by, but simpler than, https://github.com/FutureMind/drf-friendly-errors
    which is currently unmaintained and not compatible with latest DRF.
    """
    # Call rest_framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Restructure the standard error response
        # so it has a consistent shape
        data = {}

        message = getattr(exc, "default_detail", None)
        if "detail" in response.data:
            message = str(response.data["detail"])
            del response.data["detail"]
        data["message"] = message

        errors = []
        for key, value in response.data.items():
            message = (
                ". ".join([str(item) for item in value])
                if isinstance(value, list)
                else str(value)
            )
            error = {"field": key, "message": message}
            errors.append(error)
        if len(errors):
            data["errors"] = errors

        response.data = data

        return response

    # rest_framework did not handle this exception so
    # generate a API response to prevent it from getting handled by the
    # default Django HTML-generating 500 handler
    data = {"message": str(exc)}
    if settings.DEBUG:
        data["traceback"] = traceback.format_exc()
    if hasattr(settings, "SENTRY_DSN") and settings.SENTRY_DSN:
        capture_exception(exc)
    return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
