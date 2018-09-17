"""
Permission models implementing permission which a user can have in a project.
view--  Can read, but not change, the content of project documents.
         Can update ‘variables’ in the document e.g. input boxes, range sliders and see the resulting updates.
         This is the permission for a public project for an unauthenticated (aka anonymous) user.
comment -- Can add a comment to project documents.
           This is the permission for a public project for an authenticated user (i.e. a user needs to be logged in to leave a comment on a public project).
suggest -- Can suggest changes to project documents (all content including code).
edit -- Can change the content of project documents.
manage -- Can add/remove collaborators and change their permissions for a project.
          But can not give any collaborators the ‘owner’ permission.
own -- Can delete the project.
      Can give the ‘owner’ permission to a collaborator on the project.
"""

import typing

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet, Q
from django.db.models.signals import post_save

from accounts.models import Team
from projects.models import Project
from lib.enum_choice import EnumChoice


class ProjectPermissionType(EnumChoice):
    VIEW = 'view'
    COMMENT = 'comment'
    SUGGEST = 'suggest'
    EDIT = 'edit'
    MANAGE = 'manage'
    OWN = 'own'


class ProjectPermission(models.Model):
    type = models.TextField(
        null=False,
        blank=False,
        choices=ProjectPermissionType.as_choices(),
        unique=True)

    def as_enum(self) -> ProjectPermissionType:
        return ProjectPermissionType(self.type)

    def __str__(self):
        return self.type


class ProjectRole(models.Model):
    name = models.TextField(null=False, unique=True)
    permissions = models.ManyToManyField(ProjectPermission, related_name='roles')

    def permissions_text(self) -> typing.Set[str]:
        return {permission.type for permission in self.permissions.all()}

    def permissions_types(self) -> typing.Set[ProjectPermissionType]:
        return set(map(lambda p: ProjectPermissionType(p), self.permissions_text()))

    def __str__(self):
        return self.name


class ProjectAgentRole(models.Model):
    """
    Model connecting `Users` or `Teams` (`Agents`) with their `Roles` (permissions) in the `Project`
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.DO_NOTHING
    )

    agent_id = models.PositiveIntegerField(db_index=True)  # ID of the Team or User
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

    @classmethod
    def filter_with_agent(cls, agent: typing.Union[User, Team], **kwargs) -> QuerySet:
        """
        Since this model users `GenericForeignKey` we can't filter on `agent` using built in filter(), so this is a
        helper method to transform agent into id/content type
        """
        kwargs['agent_id'] = agent.pk
        kwargs['content_type'] = ContentType.objects.get_for_model(agent)
        return cls.objects.filter(**kwargs)

    @classmethod
    def filter_with_user_teams(cls, user: typing.Optional[User] = None,
                               teams: typing.Optional[typing.Iterable[Team]] = None, **kwargs) -> QuerySet:
        """
        Filter for all `ProjectAgentRole` for the `user` or any of the `teams`.
        """
        if user:
            user_query = Q(agent_id=user.pk, content_type=ContentType.objects.get_for_model(User))
        else:
            user_query = None

        if teams:
            team_query = None
            for team in teams:
                single_team_query = Q(agent_id=team.pk, content_type=ContentType.objects.get_for_model(Team))
                if team_query:
                    team_query = team_query | single_team_query
                else:
                    team_query = single_team_query
        else:
            team_query = None

        if team_query and user_query:
            agent_query = user_query | team_query
        elif team_query:
            agent_query = team_query
        elif user_query:
            agent_query = user_query
        else:
            agent_query = None

        if not kwargs and not agent_query:
            raise ValueError("Can't query for ProjectAgentRole because there are no filters.")

        if agent_query:
            return cls.objects.filter(agent_query, **kwargs)

        return cls.objects.filter(**kwargs)

    @property
    def team(self) -> Team:
        if self.content_type != ContentType.objects.get_for_model(Team):
            raise ValueError("Agent for this role mapping is not a Team")
        return Team.objects.get(pk=self.agent_id)

    @property
    def user(self) -> User:
        if self.content_type != ContentType.objects.get_for_model(User):
            raise ValueError("Agent for this role mapping is not a User")
        return User.objects.get(pk=self.agent_id)


    def record_permission(sender, instance, created, *args, **kwargs):
        content_type = instance.creator
        project = instance
        owner_role = ProjectRole.objects.get(name='Owner')
        if sender is Project and created:
            ProjectAgentRole.objects.create(content_type, project, role=owner_role)


    post_save.connect(record_permission, sender=Project)
