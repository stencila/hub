from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from accounts.api.views import AccountsViewSet
from manager.ui import helpers


def viewset(request: HttpRequest, *args, **kwargs):
    """Create an account view set for the request."""
    return helpers.viewset(AccountsViewSet, request, *args, *kwargs)


def list_orgs(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    List organizational accounts as "/orgs".

    Filters the default queryset to only include organizational accounts.
    """
    queryset = (
        viewset("list", request, args, kwargs).get_queryset().filter(user__isnull=True)
    )
    return render(request, "accounts/list.html", dict(accounts=queryset, is_orgs=True))


def list_users(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    List personal accounts as "/users".

    Filters the default queryset to only include personal accounts.
    """
    queryset = (
        viewset("list", request, args, kwargs).get_queryset().filter(user__isnull=False)
    )
    return render(request, "accounts/list.html", dict(accounts=queryset, is_users=True))


@login_required
def create(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Create an account."""
    serializer = viewset("create", request, args, kwargs).get_serializer()
    return render(request, "accounts/create.html", dict(serializer=serializer))


def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Retrieve an account."""
    object = viewset("retrieve", request, args, kwargs).get_object()
    return render(request, "accounts/retrieve.html", dict(account=object))


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an account."""
    serializer = viewset("update", request, args, kwargs).get_serializer()
    return render(request, "accounts/update.html", dict(serializer=serializer))
