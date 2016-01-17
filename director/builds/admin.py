from django.contrib import admin

from builds.models import Build


class BuildAdmin(admin.ModelAdmin):

    list_display = ('id', 'package', 'flavour', 'version', 'commit', 'platform', 'get_username', 'datetime')

    def get_username(self, obj):
        return obj.user.username if obj.user else None
    get_username.admin_order_field = 'user__username'
    get_username.short_description = 'Username'

admin.site.register(Build, BuildAdmin)
