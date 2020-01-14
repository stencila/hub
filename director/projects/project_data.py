import typing

from django.contrib.auth.models import User

from accounts.db_facade import fetch_accounts_for_user
from projects.permission_models import ProjectAgentRole
from projects.project_models import Project


class FilterOption(typing.NamedTuple):
    key: str
    label: str
    description: str


FILTER_OPTIONS = (
    FilterOption('created', 'Created by me', 'Projects that were created by you.'),
    FilterOption('account', 'Account projects', 'Projects owned by Accounts to which you belong.'),
    FilterOption('shared', 'Shared with me', 'Projects to which you or one of your Teams have access.'),
    FilterOption('public', 'Public', 'Projects that are publicly visible.')
)

FILTER_LOOKUP = {f.key: f for f in FILTER_OPTIONS}


class ProjectFetchResult(typing.NamedTuple):
    filter: FilterOption
    projects: typing.Iterable[Project]
    available_results: int
    remaining_results: typing.Optional[int]


def get_projects(user: User, filter_key: typing.Optional[str],
                 limit: typing.Optional[int] = None) -> ProjectFetchResult:
    if not user.is_authenticated:
        projects = Project.objects.filter(public=True)
        filter_key = 'public'
    else:
        if filter_key == 'account':
            accounts = fetch_accounts_for_user(user)
            projects = Project.objects.filter(account__in=accounts)
        elif filter_key == 'shared':
            project_ids = ProjectAgentRole.filter_with_user_teams(user=user).exclude(
                project__creator=user).values_list('project', flat=True)
            projects = Project.objects.filter(pk__in=project_ids)
            # all_projects = map(lambda par: par.project, roles)
            # projects = filter(lambda proj: proj.creator != user, all_projects)
        elif filter_key == 'public':
            projects = Project.objects.filter(public=True)
        else:
            filter_key = 'created'
            projects = Project.objects.filter(creator=user)

    available_results = projects.count()

    if limit:
        remaining_results = available_results - limit
        projects = projects[:limit]
    else:
        remaining_results = None

    return ProjectFetchResult(FILTER_LOOKUP[filter_key], projects, available_results, remaining_results)
