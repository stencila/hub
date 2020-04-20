from django.contrib import admin

from jobs.models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "project_id",
        "created",
        "began",
        "ended",
        "status",
        "method",
        "queue",
        "worker",
    ]
    show_full_result_count = False
