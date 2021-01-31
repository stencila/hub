from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from accounts.models import Account, AccountTeam, AccountTier, AccountUser
from accounts.tasks import set_image_from_socialaccounts


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin interface for accounts."""

    list_display = ["name", "creator", "created", "is_personal", "tier"]
    list_select_related = ["creator"]
    list_filter = ["tier"]
    search_fields = ["name"]
    actions = ["set_image_from_socialaccounts", "downgrade_to_tier1"]

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

    def downgrade_to_tier1(self, request, queryset):
        """
        Downgrades the selected accounts to Tier 1 (Free).

        Uses a confirmation page to make sure the
        staff member wants to do that!.
        """
        if "apply" in request.POST:
            # Downgrades to tier 1
            queryset.update(tier_id=1)

            # Redirect to admin view with message
            self.message_user(
                request, "Downgraded {} accounts to tier 1".format(queryset.count())
            )
            return HttpResponseRedirect(request.get_full_path())

        return render(
            request,
            "accounts/admin/accounts_downgrade_confirm.html",
            context={"accounts": queryset},
        )

    downgrade_to_tier1.short_description = "Downgrade to Tier 1"  # type: ignore


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
        "product",
        "active",
        "account_users",
        "account_teams",
        "projects_public",
        "projects_private",
        "file_downloads_month",
        "job_runtime_month",
        "dois_created_month",
    ]
