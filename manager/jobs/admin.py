from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from jobs.models import (
    Job,
    Pipeline,
    PipelineSchedule,
    Queue,
    Worker,
    WorkerHeartbeat,
    Zone,
)


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
        "queue_id",
        "worker",
    ]
    list_filter = ["status", "method"]
    show_full_result_count = False

    actions = ["cancel"]

    def cancel(self, request, queryset):
        """
        Cancel the selected jobs.

        Uses a confirmation page to make sure the
        staff member wants to cancel the jobs.
        """
        if "apply" in request.POST:
            # Cancel the jobs
            for job in queryset.all():
                job.cancel()

            # Redirect to admin view with message
            self.message_user(request, "Cancelled {} jobs".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())

        return render(
            request, "jobs/admin/jobs_cancel_confirm.html", context={"jobs": queryset}
        )

    cancel.short_description = "Cancel selected jobs"


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


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    """Admin interface for zones."""

    list_display = [
        "name",
        "zone",
        "priority",
        "untrusted",
        "interrupt",
    ]


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    """Admin interface for workers."""

    list_display = [
        "id",
        "hostname",
        "created",
        "started",
        "updated",
        "active",
    ]


@admin.register(WorkerHeartbeat)
class WorkerHeartbeatAdmin(admin.ModelAdmin):
    """Admin interface for worker heartbeats."""

    list_display = [
        "worker_id",
        "time",
        "active",
        "processed",
        "load",
    ]


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    """Admin interface for zones."""

    list_display = [
        "id",
        "account",
        "name",
    ]
    list_select_related = ["account"]
