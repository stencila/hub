import typing

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lib.enum_choice import EnumChoice


class ProjectPermissionType(EnumChoice):
    VIEW = 'view'
    COMMENT = 'comment'
    SUGGEST = 'suggest'
    EDIT = 'edit'
    MANAGE = 'manage'
    OWN = 'own'


class ProjectPermission(models.Model):
    type = models.TextField(null=False, blank=False, choices=ProjectPermissionType.as_choices(), unique=True)

    def as_enum(self) -> ProjectPermissionType:
        return ProjectPermissionType(self.type)


class ProjectRole(models.Model):
    name = models.TextField(null=False, unique=True)
    permissions = models.ManyToManyField(ProjectPermission, related_name='roles')

    def permissions_text(self) -> typing.Set[str]:
        return {permission.type for permission in self.permissions.all()}

    def permissions_types(self) -> typing.Set[ProjectPermissionType]:
        return set(map(lambda p: ProjectPermissionType(p.type), self.permissions_text()))


class UserProjectRole(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=False,
        related_name='project_roles',
        db_index=True
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.DO_NOTHING
    )

    agent_id = models.PositiveIntegerField()  # ID of the Team or User
    agent = GenericForeignKey('content_type', 'agent_id')  # Team or User

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=False,
        related_name='roles',
        db_index=True
    )

    role = models.ForeignKey(
        ProjectRole,
        on_delete=models.CASCADE,
        related_name='+'
    )


def user_has_project_permission(user: User, project: 'Project', permission_type: ProjectPermissionType) -> bool:
    """Example implementation of checking for a specific permission on a `Project` for a `User`"""
    project_roles = ProjectRole.objects.filter(user=user, project=project)

    for project_role in project_roles:
        if permission_type in project_role.role.permissions_types():
            return True

    return False


def user_can_edit_project(user: User, project: 'Project') -> bool:
    return user_has_project_permission(user, project, ProjectPermissionType.EDIT)
