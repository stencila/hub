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

    if account:
        account_name = account.name
    elif url_kwargs:
        if 'account_name' in url_kwargs:
            account_name = url_kwargs['account_name']
        elif 'pk' in url_kwargs:
            account = typing.cast(Account, Account.objects.get(pk=url_kwargs['pk']))
            account_name = account.name
        else:
            raise TypeError('No Account PK or Name could be found in url_kwargs')
    else:
        raise TypeError('One of url_kwargs or account must be set.')

    view_name += '_slug'
    args.insert(0, account_name)

    return view_name, args
