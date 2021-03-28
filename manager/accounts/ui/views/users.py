from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from accounts.api.views import AccountsUsersViewSet


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an account."""
    viewset = AccountsUsersViewSet.init("list", request, args, kwargs)
    context = viewset.get_response_context()
    return render(request, "accounts/users/update.html", context)
