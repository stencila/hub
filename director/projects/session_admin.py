from django.contrib import admin

from projects.session_models import SessionRequest
from .models import Session, SessionParameters


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass


@admin.register(SessionParameters)
class SessionParametersAdmin(admin.ModelAdmin):
    pass


@admin.register(SessionRequest)
class SessionRequestAdmin(admin.ModelAdmin):
    pass
