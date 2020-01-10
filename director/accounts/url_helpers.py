import typing

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from accounts.models import Account


def account_redirect(view_name: str, args: typing.Optional[typing.List[typing.Any]] = None,
                     url_kwargs: typing.Optional[dict] = None,
                     account: typing.Optional[Account] = None) -> HttpResponse:
    """
    Build a redirect response for the account, automatically use slug URL if possible mode.

    Parameters are documented in the `accountt_url_parameters` below.
    """
    view_name, args = account_url_parameters(view_name, args, url_kwargs, account)

    return redirect(view_name, *args)


def account_url_reverse(view_name: str, args: typing.Optional[typing.List[typing.Any]] = None,
                        url_kwargs: typing.Optional[dict] = None, account: typing.Optional[Account] = None) -> str:
    """
    Build a URL (path) for the project  automatically use slug URL if possible mode.

    Parameters are documented in the `project_url_parameters` below.
    """
    view_name, args = account_url_parameters(view_name, args, url_kwargs, account)

    return reverse(view_name, args=args)


def account_url_parameters(view_name: str, args: typing.Optional[typing.List[typing.Any]],
                           url_kwargs: typing.Optional[dict],
                           account: typing.Optional[Account]) -> typing.Tuple[str, typing.List[str]]:
    """
    Generate the view_name with a _slug prefix if in slug mode, and prepend the correct parameters to args.

    This should be called with the `url_kwargs` (which will contain either slugs or account pk) or the account. Only one
    of these should be passed in. The view_name will have _slug appended to it and returned if we are in slug mode,
    otherwise it will be returned as is.

    The args list will be updated with either PK or slugs prepended to it.
    """
    args = args or []
    account_slug = None
    account_pk = None
    if (url_kwargs is None) == (account is None):
        raise TypeError('One of url_kwargs or account must be set, not both or neither.')
    if url_kwargs:
        # kwargs mode
        if 'account_slug' in url_kwargs:
            account_slug = url_kwargs['account_slug']
        else:
            account_pk = url_kwargs.get('pk')

        if account_pk is None and account_slug is None:
            raise TypeError('No Account PK or Slug could be found in url_kwargs')
    else:
        # Account is not None since we checked this above
        # but mypy does not understand this
        if account is None:
            raise TypeError('Account is None even though we checked this above! Thanks MyPy')

        if account.slug:
            account_slug = account.slug
        else:
            account_pk = account.pk

        # no need to check that we have a values as account.pk should always be set
    if account_slug:
        view_name += '_slug'
        args.insert(0, account_slug)
    else:
        args.insert(0, account_pk)
    return view_name, args
