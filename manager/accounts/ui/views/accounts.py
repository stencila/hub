from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect as redir
from django.shortcuts import render

from accounts.api.views import AccountsViewSet
from accounts.models import AccountTier
from accounts.quotas import AccountQuotas
from accounts.ui.forms import AccountImageForm
from projects.api.views.projects import ProjectsViewSet


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
    account_viewset = AccountsViewSet.init("retrieve", request, args, kwargs)
    account = account_viewset.get_object()

    # Show projects that the request user has read access to, and
    # - for personal accounts, that the account user is a member of
    # - for organizational accounts, only those owned by the account
    # ie. will only show private projects if the request user has access to it
    projects_viewset = ProjectsViewSet.init("retrieve", request, args, kwargs)
    projects = projects_viewset.get_queryset()
    if account.is_personal:
        projects = projects.filter(agents__user=account.user_id)
    else:
        projects = projects.filter(account=account)

    return render(
        request,
        "accounts/retrieve.html",
        dict(
            account=account,
            role=account.role,
            projects=projects,
            meta=account.get_meta(),
        ),
    )


@login_required
def profile(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an account profile."""
    viewset = AccountsViewSet.init("partial_update", request, args, kwargs)
    account = viewset.get_object()
    serializer = viewset.get_serializer(account)
    update_image_form = AccountImageForm()
    return render(
        request,
        "accounts/profile.html",
        dict(
            account=account,
            role=account.role,
            serializer=serializer,
            update_image_form=update_image_form,
        ),
    )


@login_required
def profile_image(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Update an account's profile image.

    Also updates the cached URL of the user's image in the session storage.
    See the `session_storage` middleware for how this is set initially.
    """
    if request.method == "POST":
        viewset = AccountsViewSet.init("partial_update", request, args, kwargs)
        account = viewset.get_object()
        form = AccountImageForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()

            if account.is_personal:
                if request.session and "user" in request.session:
                    request.session["user"][
                        "image"
                    ] = request.user.personal_account.image.medium
                    request.session.modified = True

            return redir("ui-accounts-profile", account.name)
        raise RuntimeError("Error attempting to save the account image.")
    else:
        raise Http404


@login_required
def publishing(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an account publishing settings."""
    viewset = AccountsViewSet.init("partial_update", request, args, kwargs)
    account = viewset.get_object()
    serializer = viewset.get_serializer(account)
    return render(
        request,
        "accounts/publishing.html",
        dict(account=account, role=account.role, serializer=serializer),
    )


@login_required
def plan(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Get the account usage relative to current and other plans.

    This uses the `update_plan` action to check permission: although
    this view does not change the plan, we only want MANAGER or OWNER
    to see usage etc.
    """
    viewset = AccountsViewSet.init("update_plan", request, args, kwargs)
    account = viewset.get_object()
    usage = AccountQuotas.usage(account)
    tiers = AccountTier.objects.order_by("id").all()
    fields = AccountTier.fields()
    return render(
        request,
        "accounts/plan.html",
        dict(
            account=account,
            role=account.role,
            usage=usage,
            tier=account.tier,
            tiers=tiers,
            fields=fields,
        ),
    )

@login_required
def subscribe(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Subscribe to a particular plan.

    Creates a new `account.customer` if necessary.
    """
    viewset = AccountsViewSet.init("update_plan", request, args, kwargs)
    account = viewset.get_object()

    customer = account.get_customer()

    return render(
        request,
        "accounts/subscribe.html",
        dict(
            account=account
        ),
    )
