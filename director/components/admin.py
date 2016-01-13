from django.contrib import admin

from reversion.admin import VersionAdmin

from components.models import Component, Address, Key


class ComponentAdmin(VersionAdmin):

    list_display = ('id', 'address', 'type', 'title', 'initialised', 'updated', 'published', 'views', 'stars', 'forks')
    actions = ['init', 'update']

    def init(self, request, queryset):
        for com in queryset:
            com.initialise()
        self.message_user(request, "%s components initialised" % len(queryset))
    init.short_description = 'Initialise component repo'

    def update(self, request, queryset):
        for com in queryset:
            com.update()
        self.message_user(request, "%s components updated." % len(queryset))
    update.short_description = 'Update component'

admin.site.register(Component, ComponentAdmin)


class AddressAdmin(admin.ModelAdmin):

    list_display = ('id', 'public')

admin.site.register(Address, AddressAdmin)


class KeyAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'address', 'type', 'action')

admin.site.register(Key, KeyAdmin)
