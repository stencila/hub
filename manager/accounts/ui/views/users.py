from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from accounts.api.views import AccountsViewSet


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an account."""
    viewset = AccountsViewSet.init("update", request, args, kwargs)
    account, role = viewset.get_account_role()
    return render(
        request, "accounts/users/update.html", dict(account=account, role=role),
    )
