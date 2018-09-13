import typing

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from accounts.models import Team
from projects.permission_models import ProjectRole, ProjectAgentRole, ProjectPermissionType
from projects.project_models import Project

User = get_user_model()

READ_ONLY_PROJECT_ROLE_NAME = 'Viewer'


class ProjectFetchResult(typing.NamedTuple):
    """
    Represents the result of fetching a project for a particular agent (`User` or `Team`), includes:
    -- agent_roles: roles the current agent (`User`/`Team`) has for the `Project``
    -- agent_permissions: all permissions the current agent (`User`/`Team`) has for the `Account`, i.e. combined
        permissions of all roles
    """
    project: Project
    agent_roles: typing.Set[ProjectRole]
    agent_permissions: typing.Set[ProjectPermissionType]


def add_roles_to_permissions_sets(roles_set: typing.Set[ProjectRole],
                                  permissions_set: typing.Set[ProjectPermissionType], role: ProjectRole) -> None:
    if role not in roles_set:
        roles_set.add(role)
        for permission_type in role.permissions_types():
            permissions_set.add(permission_type)


def fetch_project_for_user(user: User, project_pk: int) -> ProjectFetchResult:
    project = get_object_or_404(Project, pk=project_pk)
    user_teams = Team.objects.filter(members=user) if user.is_authenticated else []

    project_agent_roles = ProjectAgentRole.filter_with_user_teams(user, user_teams, project=project)

    roles: typing.Set[ProjectRole] = set()
    permissions: typing.Set[ProjectPermissionType] = set()

    if project_agent_roles.count():
        for project_agent_role in project_agent_roles:
            add_roles_to_permissions_sets(roles, permissions, project_agent_role.role)
    elif project.public:
        read_only_role = ProjectRole.objects.get(name=READ_ONLY_PROJECT_ROLE_NAME)

        add_roles_to_permissions_sets(roles, permissions, read_only_role)

    return ProjectFetchResult(project, roles, permissions)
