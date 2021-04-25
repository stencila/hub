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
from manager.admin import InputFilter


class JobCreatorUsernameFilter(InputFilter):
    """
    Filter repos by the username of their creator.
    """

    parameter_name = "creator"
    title = "Creator"

    def queryset(self, request, queryset):
        """
        Filter the list of jobs by creator username.
        """
        name = self.value()
        if name is not None:
            return queryset.filter(creator__username=name)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin interface for jobs."""

    list_display = [
        "id",
        "parent_id",
        "project_id",
        "creator",
        "created",
        "began",
        "ended",
        "status",
        "method",
        "queue_id",
    ]
    list_select_related = ["creator"]
    list_filter = [JobCreatorUsernameFilter, "created", "status", "method"]
    show_full_result_count = False

    # Page load speed is improved by making fields that do look ups readonly
    # Most of these you never want to edit anyway.
    readonly_fields = [
        "created",
        "began",
        "ended",
        "runtime",
        "urls",
        "users",
        "anon_users",
        "worker",
        "retries",
        "callback_type",
        "callback_id",
        "callback_method",
    ]
    raw_id_fields = ["project", "snapshot", "creator", "queue", "parent"]
    exclude = ["secrets"]

    actions = ["cancel"]

    @admin.action(description="Cancel selected jobs")
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
        "finished",
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
