from rest_framework import exceptions, status


class AccountQuotaExceeded(exceptions.APIException):
    """
    A custom API exception for when an account quota is exceeded.

    Should be instantiated with a dictionary of details of
    the quota that was exceeded.
    """

    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = "An account quota was exceeded"


class SocialTokenMissing(exceptions.APIException):
    """
    A custom API exception for when a user is missing a social account token.

    Should be instantiated with a dictionary of the scoial
    auth provider and a message.
    """

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "No token available for a social account provider."


class ConflictError(exceptions.APIException):
    """
    A custom API exception for conflict errors.

    Should be used when the request data is valid but fails
    due to a conflict of some sort e.g. a uniqueness constraint.
    Such an exception does not exist in DRF. Although see:
    https://github.com/encode/django-rest-framework/issues/1848
    """

    status_code = status.HTTP_409_CONFLICT
    default_detail = "A conflict occurred"
