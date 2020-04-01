from typing import Set

from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

# Unregister the default user model admin
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """A custom admin interface for User instances."""

    list_display = [
        'username',
        'first_name',
        'last_name',
        'date_joined',
        'last_login',
        'is_staff',
    ]

    readonly_fields = [
        'last_login',
        'date_joined',
    ]

    def get_form(self, request, obj=None, **kwargs):
        """
        Restrict the fields that staff can change.

        For more on the why and how of this see https://realpython.com/manage-users-in-django-admin/
        """
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields: Set[str] = set()

        if not is_superuser:
            disabled_fields |= {
                # Prevent non-superusers from changing usernames
                'username',
                # Prevent non-superusers from making a user staff or
                # a superuser
                'is_staff',
                'is_superuser',
                # Prevent non-superusers from granting permissions to
                # specific users or groups
                'user_permissions',
                'groups'
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form

    def save_related(self, request, form, formsets, change):
        """
        Ensure that staff, and only staff, are members of the "Staff" permissions group.

        This does not grant any permissions to the staff group.
        That is left to the `admin` user to manage via the admin interface.
        """
        instance = form.instance
        if instance.is_staff and instance.groups.filter(name='Staff').count() == 0:
            group, created = Group.objects.get_or_create(name='Staff')
            instance.groups.add(group)
        elif not instance.is_staff and instance.groups.filter(name='Staff').count() > 0:
            group = Group.objects.get(name='Staff')
            instance.groups.remove(group)
