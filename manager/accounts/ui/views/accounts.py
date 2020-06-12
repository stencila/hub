from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect as redir
from django.shortcuts import render

from accounts.api.views import AccountsViewSet


def redirect(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Redirect from an account `id` URL to an account `name` URL.
    
    For instances where we need to redirect to the account using `id`
    (e.g. because its name may have changed in a form).
    This uses `get_object` to ensure the same access control applies
    to the redirect.
    """
    viewset = AccountsViewSet.init("retrieve", request, args, kwargs)
    account = viewset.get_object()
    return redir("/{0}{1}".format(account.name, kwargs["rest"]))


def list_orgs(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    List organizational accounts as "/orgs".

    Filters the default queryset to only include organizational accounts.
    """
    viewset = AccountsViewSet.init("list", request, args, kwargs)
    accounts = viewset.get_queryset().filter(user__isnull=True)
    return render(request, "accounts/list_orgs.html", dict(accounts=accounts))


def list_users(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    List personal accounts as "/users".

    Filters the default queryset to only include personal accounts.
    """
    viewset = AccountsViewSet.init("list", request, args, kwargs)
    accounts = viewset.get_queryset().filter(user__isnull=False)
    return render(request, "accounts/list_users.html", dict(accounts=accounts))


@login_required
def create(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Create an account."""
    viewset = AccountsViewSet.init("create", request, args, kwargs)
    serializer = viewset.get_serializer()
    return render(request, "accounts/create.html", dict(serializer=serializer))


def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Retrieve an account."""
    viewset = AccountsViewSet.init("retrieve", request, args, kwargs)
    account = viewset.get_object()
    projects = account.projects.all()
    return render(
        request,
        "accounts/retrieve.html",
        dict(account=account, role=account.role, projects=projects),
    )


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an account."""
    viewset = AccountsViewSet.init("partial_update", request, args, kwargs)
    account = viewset.get_object()
    serializer = viewset.get_serializer(account)
    return render(
        request,
        "accounts/update.html",
        dict(serializer=serializer, account=account, role=account.role),
    )
