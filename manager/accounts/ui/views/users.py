from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from accounts.api.views import AccountsViewSet


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an account."""
    viewset = AccountsViewSet.init("partial_update", request, args, kwargs)
    account = viewset.get_object()
    return render(
        request, "accounts/users/update.html", dict(account=account, role=account.role),
    )
