from django.contrib import admin

from snippets.models import Snippet


class SnippetAdmin(admin.ModelAdmin):

    list_display = ('id',)

    def get_username(self, obj):
        return obj.user.username if obj.user else None
    get_username.admin_order_field = 'user__username'
    get_username.short_description = 'Username'

admin.site.register(Snippet, SnippetAdmin)
