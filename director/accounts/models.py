"""
Models implementing Stencila Hub `Accounts` against which the usage of the computational
resources is metered.
"""

import typing

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import post_save

from lib.enum_choice import EnumChoice


class AccountPermissionType(EnumChoice):
    """
    There are two types of `Permissions` to the `Account`:

    1) Modification allows to link a new Project to the Account,

    2) Administration is a higher level of permission type. It allows to
    manage teams (create and alter membership), delete Accounts; update
    the billing details for the Account and give other Account Members
    administrative permission.
    """
    MODIFY = 'modify'
    ADMINISTER = 'administer'


class Account(models.Model):
    """
    `Accounts` are the entity against which resource usage is metered, and
    can be billed if it exceeds the free allocation.

    Every user has their own `Personal Account` - created by `create_personal_account_for_user`.

    Users can create additional Accounts linking them to multiple Projects and Teams.
    """
    name = models.TextField(
        null=False,
        blank=False,
        unique=True,
        help_text='The name of the account (required).'
    )

    logo = models.ImageField(
        null=True,
        blank=True,
        help_text='A logo for the account'
    )

    def get_administrators(self) -> typing.Iterable[User]:
        """
        Returns users who have administrative permissions on the account.
        """
        ownership_roles = set()  # cache the roles that have ownership perms
        users = set()

        for user_role in self.user_roles.all():
            user_has_role = False

            if user_role.role.pk in ownership_roles:
                user_has_role = True
            elif AccountPermissionType.ADMINISTER in user_role.role.permissions_types():
                ownership_roles.add(user_role.role.pk)
                user_has_role = True

            if user_has_role:
                users.add(user_role.user)

        return users

    def __str__(self) -> str:
        return self.name if self.name else 'Account #{}'.format(self.pk)


class Team(models.Model):
    """
    Team is can be formed by one or more Users. Each User can be a member of multiple Teams.
    Each Team is linked to exactly one Account.
    """
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text='Account to which the Team is linked to. Each Team can be linked to only one account.',
        related_name='teams'
    )

    name = models.TextField(
        blank=False,
        null=False,
        help_text='The name of the team (required).'
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text='Team description (optional).'
    )

    members = models.ManyToManyField(
        'auth.User',
        help_text='Team members. Each User can be a member of multiple Teams.'
    )

    def __str__(self) -> str:
        return self.name


class AccountPermission(models.Model):
    """
    Model implementing types of the permissions to the `Account`.
    """
    type = models.TextField(
        null=False,
        blank=False,
        choices=AccountPermissionType.as_choices(),
        unique=True,
        help_text='Permissions to the Account: Administer or Modify (required).'
    )

    def __str__(self) -> str:
        return self.type


class AccountRole(models.Model):
    """
    Roles linked to the Account, depending on their `AccountPermissionType`.
    """
    name = models.TextField(
        null=False,
        blank=False,
        help_text='Roles which users can have assigned to the Account: Admin and Member (required).'
    )

    permissions = models.ManyToManyField(
        AccountPermission,
        related_name='roles',
        help_text='User Permissions to the Account: Administrator or Account Member.'
    )

    def permissions_text(self) -> typing.Set[str]:
        return {permission.type for permission in self.permissions.all()}

    def permissions_types(self) -> typing.Set[AccountPermissionType]:
        return set(map(lambda p: AccountPermissionType(p), self.permissions_text()))

    @classmethod
    def roles_with_permission(cls, permission_type: AccountPermissionType) -> QuerySet:
        """Query for a list of `AccountRoles` that have the given permission_type `AccountPermissionType`."""
        permission = AccountPermission.objects.get(type=permission_type.value)
        return cls.objects.filter(permissions=permission)

    def __str__(self) -> str:
        return self.name


class AccountUserRole(models.Model):
    """
    Model connecting `Users` with their `Roles` in the `Accounts`.
    """
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=False,
        related_name='account_roles',
        db_index=True
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='user_roles',
        db_index=True
    )

    role = models.ForeignKey(
        AccountRole,
        on_delete=models.CASCADE,
        related_name='+'
    )

    class Meta:
        unique_together = (('user', 'account'),)


def create_personal_account_for_user(sender, instance, created, *args, **kwargs):
    """
    Called when a new `User` is created and saved. Makes sure each user has a Personal `Account` that
    they are an `Account admin` on so that their `Projects` can be linked to
    an `Account`.
    """
    if sender is User and created:
        account = Account.objects.create(name='{}\'s Personal Account'.format(instance.username))
        admin_role = AccountRole.objects.get(name='Account admin')
        AccountUserRole.objects.create(role=admin_role, account=account, user=instance)


post_save.connect(create_personal_account_for_user, sender=User)
