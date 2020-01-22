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

    if url_kwargs:
        # kwargs mode
        if 'account_name' in url_kwargs and 'project_name' in url_kwargs:
            account_name = url_kwargs['account_name']
            project_name = url_kwargs['project_name']
        else:
            project_pk = url_kwargs.get('pk', url_kwargs.get('project_pk'))

            if project_pk is None:
                raise TypeError('No Project PK or Names could be found in url_kwargs')

            project = typing.cast(Project, Project.objects.get(pk=project_pk))
            account_name = project.account.name
            project_name = project.name
    elif project is not None:
        account_name = project.account.name
        project_name = project.name
    else:
        raise TypeError('Project is None')

        # no need to check that we have a values as project.pk should always be set
    view_name += '_slug'
    args.insert(0, project_name)
    args.insert(0, account_name)
    return view_name, args
