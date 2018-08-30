import typing

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from lib.enum_choice import EnumChoice


class AccountPermissionType(EnumChoice):
    MODIFY = 'modify'
    ADMINISTER = 'administer'


class Account(models.Model):
    name = models.TextField()

    def get_administrators(self) -> typing.Iterable[User]:
        ownership_roles = set()  # cache the roles that have ownership perms
        users = set()

        for user_role in self.user_roles:
            user_has_role = False

            if user_role.role.pk in ownership_roles:
                user_has_role = True
            elif AccountPermissionType.ADMINISTER in user_role.role.permissions_types():
                ownership_roles.add(user_role.role.pk)
                user_has_role = True

            if user_has_role:
                users.add(user_role.user)

        return users


class Team(models.Model):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE
    )

    name = models.TextField(
        blank=False,
        null=False
    )

    description = models.TextField(
        blank=True, null=True
    )

    members = models.ManyToManyField(
        'auth.User'
    )


class AccountPermission(models.Model):
    type = models.TextField(
        null=False,
        blank=False,
        choices=AccountPermissionType.as_choices(),
        unique=True
    )


class AccountRole(models.Model):
    permissions = models.ManyToManyField(
        AccountPermission, related_name='roles'
    )

    def permissions_text(self) -> typing.Set[str]:
        return {permission.type for permission in self.permissions.all()}

    def permissions_types(self) -> typing.Set[AccountPermissionType]:
        return set(map(lambda p: AccountPermissionType(p.type), self.permissions_text()))


class AccountUserRole(models.Model):
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
