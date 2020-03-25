from rest_framework.views import exception_handler


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
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Restructure the structure of the response data.
    if response is not None:
        data = {}

        message = getattr(exc, 'default_detail', None)
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
