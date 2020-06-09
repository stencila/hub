from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from accounts.api.views import AccountsViewSet


def list_orgs(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    List organizational accounts as "/orgs".

    Filters the default queryset to only include organizational accounts.
    """
    viewset = AccountsViewSet.init("list", request, args, kwargs)
    queryset = viewset.get_queryset().filter(user__isnull=True)
    return render(request, "accounts/list.html", dict(accounts=queryset, is_orgs=True))


def list_users(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    List personal accounts as "/users".

    Filters the default queryset to only include personal accounts.
    """
    viewset = AccountsViewSet.init("list", request, args, kwargs)
    queryset = viewset.get_queryset().filter(user__isnull=False)
    return render(request, "accounts/list.html", dict(accounts=queryset, is_users=True))


@login_required
def create(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Create an account."""
    viewset = AccountsViewSet.init("create", request, args, kwargs)
    serializer = viewset.get_serializer()
    return render(request, "accounts/create.html", dict(serializer=serializer))


def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Retrieve an account."""
    viewset = AccountsViewSet.init("retrieve", request, args, kwargs)
    account, role = viewset.get_account_role()
    return render(request, "accounts/retrieve.html", dict(account=account, role=role))


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an account."""
    viewset = AccountsViewSet.init("update", request, args, kwargs)
    account, role = viewset.get_account_role()
    serializer = viewset.get_serializer(account)
    return render(
        request,
        "accounts/update.html",
        dict(serializer=serializer, account=account, role=role),
    )
