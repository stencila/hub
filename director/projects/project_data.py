import typing

from django.contrib.auth.models import User

from accounts.db_facade import fetch_accounts_for_user
from projects.permission_models import ProjectAgentRole
from projects.project_models import Project


def get_projects(user: User, filter_key: typing.Optional[str]) -> typing.Tuple[str, typing.Iterable[Project]]:
    if not user.is_authenticated:
        return 'public', Project.objects.filter(public=True)

    if filter_key == 'account':
        accounts = fetch_accounts_for_user(user)
        projects = Project.objects.filter(account__in=accounts)
    elif filter_key == 'shared':
        roles = ProjectAgentRole.filter_with_user_teams(user=user)
        all_projects = map(lambda par: par.project, roles)
        projects = filter(lambda proj: proj.creator != user, all_projects)
    elif filter_key == 'public':
        projects = Project.objects.filter(public=True)
    else:
        filter_key = 'created'
        projects = Project.objects.filter(creator=user)

    return filter_key, projects
