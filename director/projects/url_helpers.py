import typing

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from projects.project_models import Project


def project_redirect(view_name: str, args: typing.Optional[typing.List[typing.Any]] = None,
                     url_kwargs: typing.Optional[dict] = None,
                     project: typing.Optional[Project] = None) -> HttpResponse:
    """
    Build a redirect response for the project, automatically use slug URL if possible mode.

    Parameters are documented in the `project_url_parameters` below.
    """
    view_name, args = project_url_parameters(view_name, args, url_kwargs, project)

    return redirect(view_name, *args)


def project_url_reverse(view_name: str, args: typing.Optional[typing.List[typing.Any]] = None,
                        url_kwargs: typing.Optional[dict] = None, project: typing.Optional[Project] = None) -> str:
    """
    Build a URL (path) for the project  automatically use slug URL if possible mode.

    Parameters are documented in the `project_url_parameters` below.
    """
    view_name, args = project_url_parameters(view_name, args, url_kwargs, project)

    return reverse(view_name, args=args)


def project_url_parameters(view_name: str, args: typing.Optional[typing.List[typing.Any]],
                           url_kwargs: typing.Optional[dict],
                           project: typing.Optional[Project]) -> typing.Tuple[str, typing.List[str]]:
    """
    Generate the view_name with a _slug prefix if in slug mode, and prepend the correct parameters to args.

    This should be called with the `url_kwargs` (which will contain either slugs or project pk) or the project. Only one
    of these should be passed in. The view_name will have _slug appended to it and returned if we are in slug mode,
    otherwise it will be returned as is.

    The args list will be updated with either PK or slugs prepended to it.
    """
    args = args or []
    account_slug = None
    project_slug = None
    project_pk = None
    if (url_kwargs is None) == (project is None):
        raise TypeError('One of url_kwargs or project must be set, not both or neither.')
    if url_kwargs:
        # kwargs mode
        if 'account_slug' in url_kwargs and 'project_slug' in url_kwargs:
            account_slug = url_kwargs['account_slug']
            project_slug = url_kwargs['project_slug']
        else:
            project_pk = url_kwargs.get('pk', url_kwargs.get('project_pk'))

        if project_pk is None and (account_slug is None or project_slug is None):
            raise TypeError('No Project PK or Slugs could be found in url_kwargs')
    else:
        # Project is not None since we checked this above
        # but mypy does not understand this
        if project is None:
            raise TypeError('Project is None even though we checked this above! Thanks MyPy')

        if project.slug and project.account.slug:
            account_slug = project.account.slug
            project_slug = project.slug
        else:
            project_pk = project.pk

        # no need to check that we have a values as project.pk should always be set
    if account_slug and project_slug:
        view_name += '_slug'
        args.insert(0, project_slug)
        args.insert(0, account_slug)
    else:
        args.insert(0, project_pk)
    return view_name, args
