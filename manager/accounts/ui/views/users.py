from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from accounts.api.views import AccountsViewSet
from manager.ui import helpers


def viewset(request: HttpRequest, *args, **kwargs):
    """Create an account view set for the request."""
    return helpers.viewset(AccountsViewSet, request, *args, *kwargs)


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an account."""
    vs = viewset("update", request, args, kwargs)
    account, role = vs.get_account_role()
    return render(
        request, "accounts/users/update.html", dict(account=account, role=role),
    )
