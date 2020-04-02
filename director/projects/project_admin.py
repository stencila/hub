from django.contrib import admin

from .models import Project, ProjectPermission, ProjectRole, ProjectAgentRole


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "account", "name", "public"]
    list_filter = ["public"]


@admin.register(ProjectPermission)
class ProjectPermissionAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectAgentRole)
class ProjectAgentRoleAdmin(admin.ModelAdmin):
    list_display = ["id", "project", "role", "content_type", "agent_id"]
    list_filter = ["role"]
