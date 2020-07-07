from django.contrib import admin

from accounts.models import Account, AccountTeam, AccountTier, AccountUser


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin interface for accounts."""

    def is_personal(self, instance):
        """Field to display `is_personal` as a boolean."""
        return instance.is_personal

    is_personal.boolean = True  # type: ignore
    is_personal.short_description = u"Personal"  # type: ignore

    list_display = [
        "name",
        "creator",
        "created",
        "is_personal",
    ]
    list_select_related = ["creator"]


@admin.register(AccountUser)
class AccountUserAdmin(admin.ModelAdmin):
    """Admin interface for account users."""

    list_display = ["account", "user", "role"]


@admin.register(AccountTeam)
class AccountTeamAdmin(admin.ModelAdmin):
    """Admin interface for account teams."""

    list_display = ["account", "name"]


@admin.register(AccountTier)
class AccountTierAdmin(admin.ModelAdmin):
    """Admin interface for account tiers."""

    list_display = [
        "id",
        "name",
        "account_users",
        "account_teams",
        "projects_public",
        "projects_private",
    ]
