"""Helper functions for API views."""

import re
from typing import Dict, Optional, Type, Union

from django.shortcuts import get_object_or_404
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.request import Request
from rest_framework.response import Response


class HtmxMixin:

    renderer_classes = [CamelCaseJSONRenderer, TemplateHTMLRenderer]

    # If these codes are changed, they need to also be changed in
    # 'static/js/htmx-extensions.js`
    CREATED = 201
    RETRIEVED = 200
    UPDATED = 210
    DESTROYED = 211  # Can't used 204 here because htmx ignores that
    INVALID = 212

    @classmethod
    def init(
        cls: Type[viewsets.ViewSet], action: str, request: Request, args, kwargs
    ) -> viewsets.ViewSet:
        """
        Create a Django Rest Framework `ViewSet` instance for a request.

        This replicates the `as_view` method of the `ViewSetMixin` class
        so that we can re-use of the permissions and filtering logic defined
        in the DRF view sets within templated views e.g.

            viewset = AccountsViewSet.init("create", request, args, kwargs)
            serializer.get_serializer()

        """
        vs = cls()
        vs.action = action
        vs.request = request
        vs.args = args
        vs.kwargs = kwargs
        vs.format_kwarg = None
        return vs

    def accepts_html(self):
        return self.request.META.get("HTTP_ACCEPT") == "text/html"

    def get_template_names(self):
        template = self.request.META.get("HTTP_X_HX_TEMPLATE")
        if template:
            return [template]
        return ["api/_default.html"]


class HtmxListMixin:
    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List objects.

        Returns a list of objects.
        """
        queryset = self.get_queryset()

        if self.accepts_html():
            url = "?" + "&".join(
                [
                    "{}={}".format(key, value)
                    for key, value in self.request.GET.items()
                    if value
                ]
            )
            return Response({self.queryset: queryset}, headers={"X-HX-Push": url})
        else:
            pages = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pages, many=True)
            return self.get_paginated_response(serializer.data)


class HtmxCreateMixin:
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create an object.

        Returns data for the new object.
        """
        serializer = self.get_serializer(data=request.data)

        if self.accepts_html():
            if serializer.is_valid():
                serializer.save()
                status = self.CREATED
                headers = {"Location": self.get_success_url(serializer)}
            else:
                status = self.INVALID
                headers = {}

            return Response(dict(serializer=serializer), status=status, headers=headers)
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=self.CREATED)


class HtmxUpdateMixin:
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update an object.

        Returns data for the updated object.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if self.accepts_html():
            if serializer.is_valid():
                serializer.save()
                status = self.UPDATED
                headers = {"Location": self.get_success_url(serializer)}
            else:
                status = self.INVALID
                headers = {}

            return Response(
                {self.object_name: instance, "serializer": serializer},
                status=status,
                headers=headers,
            )
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=self.UPDATED)


class HtmxDestroyMixin:
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Destroy an object.

        Returns an empty response.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        if self.accepts_html():
            if serializer.is_valid():
                instance.delete()
                status = self.DESTROYED
            else:
                status = self.INVALID

            return Response(
                {self.object_name: instance, "serializer": serializer}, status=status
            )
        else:
            serializer.is_valid(raise_exception=True)
            obj.delete()
            return Response(status=self.DESTROYED)


def filter_from_ident(
    value: str, prefix: Optional[str] = None, int_key="id", str_key="name"
) -> Dict[str, Union[str, int]]:
    """
    Get a filter dictionary from an identifier.

    If the identifier looks like an integer, then
    the filter has key `id`, otherwise `name`.
    """
    if re.match(r"\d+", value):
        key = int_key
        value = int(value)
    else:
        key = str_key
    if prefix is not None:
        key = prefix + "__" + key
    return {key: value}


def get_object_from_ident(cls, value: str):
    """Get an object from an indentifier."""
    return get_object_or_404(cls, **filter_from_ident(value))
