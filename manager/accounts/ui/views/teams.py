from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from accounts.api.views import TeamsViewSet
from manager.ui import helpers


def viewset(request: HttpRequest, *args, **kwargs):
    """Create an account view set for the request."""
    return helpers.viewset(TeamsViewSet, request, *args, *kwargs)


@login_required
def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """List teams."""
    # Use `select_related` to avoid an extra query for each team
    queryset = (
        viewset("list", request, args, kwargs).get_queryset().select_related("account")
    )
    return render(request, "accounts/teams/list.html", dict(teams=queryset))


@login_required
def create(request: HttpRequest, account: str, *args, **kwargs) -> HttpResponse:
    """Create a team."""
    serializer = viewset("create", request, args, kwargs).get_serializer()
    return render(
        request,
        "accounts/teams/create.html",
        dict(serializer=serializer, account=account),
    )


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update or destroy a team."""
    serializer = viewset("update", request, args, kwargs).get_serializer()
    return render(request, "accounts/teams/update.html", dict(serializer=serializer))
