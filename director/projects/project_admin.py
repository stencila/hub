from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Project, ProjectPermission, ProjectRole, ProjectAgentRole


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'public', 'archive'
    ]
    list_filter = [
        'public'
    ]

    def archive(self, project):
        """
        Link to an archive of the project
        """
        url = reverse('project_archive', args=[project.id])
        return format_html('<a href="{}">Archive</a>'.format(url))

    archive.short_description = 'Archive'  # type: ignore


@admin.register(ProjectPermission)
class ProjectPermissionAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectAgentRole)
class ProjectAgentRoleAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'project', 'role', 'content_type', 'agent_id'
    ]
    list_filter = [
        'role'
    ]
