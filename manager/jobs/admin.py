from django.contrib import admin

from jobs.models import Job, Pipeline, PipelineSchedule, Zone


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin interface for jobs."""

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


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    """Admin interface for pipelines."""

    list_display = ["id", "project_id", "name"]


@admin.register(PipelineSchedule)
class PipelineScheduleAdmin(admin.ModelAdmin):
    """Admin interface for pipeline schedules."""

    exclude = [
        "name",
        "task",
        "args",
        "kwargs",
        "description",
        "queue",
        "exchange",
        "routing_key",
        "priority",
        "headers",
    ]


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    """Admin interface for zones."""

    list_display = [
        "id",
        "account_id",
        "name",
    ]
