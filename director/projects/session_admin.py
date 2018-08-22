from django.contrib import admin

from .models import (
    Session, SessionParameters)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass


@admin.register(SessionParameters)
class SessionParametersAdmin(admin.ModelAdmin):
    pass
