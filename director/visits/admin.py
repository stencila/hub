from django.contrib import admin

from visits.models import Visit


class VisitAdmin(admin.ModelAdmin):

    list_display = ('when', 'address', 'view', 'referer', 'ip', 'user')

admin.site.register(Visit, VisitAdmin)
