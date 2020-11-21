from django.contrib import admin

from accounts.models import Account, AccountTeam, AccountTier, AccountUser
from accounts.tasks import set_image_from_socialaccounts


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin interface for accounts."""

    list_display = ["name", "creator", "created", "is_personal", "tier"]
    list_select_related = ["creator"]
    list_filter = ["tier"]
    search_fields = ["name"]
    actions = ["set_image_from_socialaccounts"]

    def is_personal(self, instance):
        """Field to display `is_personal` as a boolean."""
        return instance.is_personal

    is_personal.boolean = True  # type: ignore
    is_personal.short_description = u"Personal"  # type: ignore

    def set_image_from_socialaccounts(self, request, queryset):
        """Set image from social accounts."""
        for account in queryset:
            set_image_from_socialaccounts.delay(account.id)

    set_image_from_socialaccounts.short_description = "Set image from social accounts"  # type: ignore


@admin.register(AccountUser)
class AccountUserAdmin(admin.ModelAdmin):
    """Admin interface for account users."""

    list_display = ["account", "user", "role"]
    list_filter = ["account", "user", "role"]
    search_fields = ["account__name", "user__username"]


@admin.register(AccountTeam)
class AccountTeamAdmin(admin.ModelAdmin):
    """Admin interface for account teams."""

    list_display = ["account", "name"]
    list_filter = ["account"]
    search_fields = ["account__name", "name"]


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
        "file_downloads_month",
        "job_runtime_month",
        "dois_created_month",
    ]
