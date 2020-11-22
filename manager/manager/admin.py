"""
Helpers for admin views.
"""

from django.contrib import admin


class InputFilter(admin.SimpleListFilter):
    """
    A filter that allows plain text input rather than a list of choices.

    See UsernameFilter below for an example of how to use this.
    From https://hakibenita.com/how-to-add-a-text-filter-to-django-admin.
    """

    template = "admin/input_filter.html"

    def lookups(self, request, model_admin):
        """
        Return the list of choices.

        Required to show the filter.
        Since there are no choices, return an empty tuple.
        """
        return ((),)

    def choices(self, changelist):
        """
        Extract all the filters that were applied to the queryset.

        Required to work with other filters.
        """
        all_choice = next(super().choices(changelist))
        all_choice["query_parts"] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class UserUsernameFilter(InputFilter):
    """
    Allow filtering by the username of the user.

    Note that this is not for filtering lists of the User
    model but rather for filtering lists of models that
    have a `user` property. List is useful because there are a lot
    of users and we don't want to list all the choices.
    """

    parameter_name = "user_username"
    title = "Username"

    def queryset(self, request, queryset):
        """
        Filter the queryset by the specified username.
        """
        username = self.value()
        if username is not None:
            return queryset.filter(user__username=username)


class ProjectNameFilter(InputFilter):
    """
    Allow filtering by the project name.
    """

    parameter_name = "project_name"
    title = "Project name"

    def queryset(self, request, queryset):
        """
        Filter the queryset by the project name.
        """
        name = self.value()
        if name is not None:
            return queryset.filter(project__name=name)
