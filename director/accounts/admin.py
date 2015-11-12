from django.contrib import admin

from accounts.models import Account, AccountType, Address


class AccountTypeAdmin(admin.ModelAdmin):

    list_display = ('id', 'name')

admin.site.register(AccountType, AccountTypeAdmin)


class AddressInline(admin.TabularInline):
    model = Address


class AccountAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'type')
    inlines = [AddressInline]

admin.site.register(Account, AccountAdmin)
