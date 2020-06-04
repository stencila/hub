"""Helper functions for UI views."""
from typing import Type

from django.http import HttpRequest
from rest_framework.viewsets import ViewSet


def viewset(
    cls: Type[ViewSet], action: str, request: HttpRequest, args, kwargs
) -> ViewSet:
    """
    Create a Django Rest Framework `ViewSet` instance for a request.

    This replicates the `as_view` method of the `ViewSetMixin` class
    so that we can re-use of the permissions and filtering logic defined
    in the DRF view sets within templated views e.g.

      serializer = viewset("create", request, args, kwargs).get_serializer()

    """
    vs = cls()
    vs.action = action
    vs.request = request
    vs.args = args
    vs.kwargs = kwargs
    vs.format_kwarg = None
    return vs
