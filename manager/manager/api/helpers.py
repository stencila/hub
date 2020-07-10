"""Helper functions for API views."""

import re
from typing import Dict, Optional, Type, Union

from django.shortcuts import get_object_or_404
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.request import Request
from rest_framework.response import Response


class HtmxMixin(GenericAPIView):  # noqa: D101

    renderer_classes = [CamelCaseJSONRenderer, TemplateHTMLRenderer]

    # If these codes are changed, they need to also be changed in
    # 'static/js/htmx-extensions.js`
    # Can't use 204 for destroyed because `htmx` ignores that code
    CREATED = 201
    RETRIEVED = 200
    UPDATED = 210
    DESTROYED = 211
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

    def accepts_html(self):  # noqa: D102
        return self.request.META.get("HTTP_ACCEPT") == "text/html"

    def get_template_names(self):  # noqa: D102
        template = self.request.META.get("HTTP_X_HX_TEMPLATE")
        if template:
            return [template]
        return ["api/_default.html"]

    def get_response_context(
        self, queryset=None, instance=None, serializer=None, **kwargs
    ):  # noqa: D102
        context = kwargs

        if queryset is not None:
            context[self.queryset_name] = queryset
        elif "queryset" in self.request.META.get("HTTP_X_HX_EXTRA_CONTEXT", ""):
            context[self.queryset_name] = self.get_queryset()

        if instance is not None:
            context[self.object_name] = instance

        if serializer is not None:
            context["serializer"] = serializer

        return context

    def get_success_url(self, serializer):
        """
        Get the URL to use in the Location header when an action is successful.

        This should only need to be overridden for `create`, because for other actions
        it is possible to directly specify which URL to redirect to (because the instance
        `id` is already available). ie. use `hx-redirect="UPDATED:{% url ....`
        """
        return None

    def get_success_headers(self, serializer):  # noqa: D102
        location = self.get_success_url(serializer)
        if location:
            headers = {"Location": location}
        else:
            headers = {}
        return headers


class HtmxListMixin(HtmxMixin):  # noqa: D101
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
            return Response(
                self.get_response_context(queryset=queryset), headers={"X-HX-Push": url}
            )
        else:
            pages = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pages, many=True)
            return self.get_paginated_response(serializer.data)


class HtmxCreateMixin(HtmxMixin):  # noqa: D101
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
                headers = self.get_success_headers(serializer)
            else:
                status = self.INVALID
                headers = {}

            return Response(
                self.get_response_context(
                    instance=serializer.instance, serializer=serializer
                ),
                status=status,
                headers=headers,
            )
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)


class HtmxRetrieveMixin(HtmxMixin):  # noqa: D101
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve an object.

        Returns data for the object.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if self.accepts_html():
            return Response(
                self.get_response_context(instance=instance, serializer=serializer),
                headers=self.get_success_headers(serializer),
            )
        else:
            return Response(serializer.data)


class HtmxUpdateMixin(HtmxMixin):  # noqa: D101
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
                headers = self.get_success_headers(serializer)
            else:
                status = self.INVALID
                headers = {}

            return Response(
                self.get_response_context(instance=instance, serializer=serializer),
                status=status,
                headers=headers,
            )
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class HtmxDestroyMixin(HtmxMixin):  # noqa: D101
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Destroy an object.

        Returns an empty response.
        """
        instance = self.get_object()

        serializer_class = self.get_serializer_class()
        if serializer_class:
            serializer = serializer_class(instance, data=request.data)
        else:
            serializer = None

        if self.accepts_html():
            if serializer and not serializer.is_valid():
                status = self.INVALID
                headers = {}
            else:
                instance.delete()
                status = self.DESTROYED
                headers = self.get_success_headers(serializer)

            return Response(
                self.get_response_context(instance=instance, serializer=serializer),
                status=status,
                headers=headers,
            )
        else:
            if serializer:
                serializer.is_valid(raise_exception=True)
            instance.delete()
            return Response(status=204)


def filter_from_ident(
    value: Union[str, int], prefix: Optional[str] = None, int_key="id", str_key="name"
) -> Dict[str, Union[str, int]]:
    """
    Get a filter dictionary from an identifier.

    If the identifier looks like an integer, then
    the filter has key `id`, otherwise `name`.
    """
    if isinstance(value, str) and re.match(r"\d+", value):
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
