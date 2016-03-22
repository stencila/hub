#  This file is part of Stencila Hub.
#  
#  Copyright (C) 2015-2016 Stencila Ltd.
#  
#  Stencila Hub is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  Stencila Hub is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  
#  You should have received a copy of the GNU Affero General Public License
#  along with Stencila Hub.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib import admin

from sessions_.models import Worker, WorkerStats, SessionType, SessionImage, Session, SessionStats, SessionLogs


class WorkerAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'provider_id', 'ip', 'active', 'cpus', 'memory',
        'get_sessions_active',
        'started', 'updated', 'stopped',
    )
    readonly_fields = ['started', 'updated', 'stopped']
    list_filter = ('active', 'cpus', 'memory')
    actions = ['launch', 'update', 'pull', 'terminate']

    def get_sessions_active(self, obj):
        return obj.sessions.filter(active=True).count()
    get_sessions_active.short_description = 'Active sessions'

    def launch(self, request, queryset):
        for worker in queryset:
            worker.launch()
        self.message_user(request, "%s workers launched." % len(queryset))
    launch.short_description = 'Launch worker'

    def update(self, request, queryset):
        for worker in queryset:
            worker.update()
        self.message_user(request, "%s workers updated." % len(queryset))
    update.short_description = 'Update worker information'

    def pull(self, request, queryset):
        for worker in queryset:
            worker.pull()
        self.message_user(request, "%s workers pulled." % len(queryset))
    pull.short_description = 'Pull all Docker images'

    def terminate(self, request, queryset):
        for worker in queryset:
            worker.terminate()
        self.message_user(request, "%s workers terminated." % len(queryset))
    terminate.short_description = 'Terminate worker'

admin.site.register(Worker, WorkerAdmin)


class WorkerStatsAdmin(admin.ModelAdmin):

    list_display = ('id', 'worker', 'time', 'sessions', 'processes', 'cpu_percent', 'mem_percent', 'disk_use_percent')
    readonly_fields = ['worker'] + list(WorkerStats.stats_fields)

admin.site.register(WorkerStats, WorkerStatsAdmin)


class SessionTypeAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'rank', 'name', 'memory', 'cpu', 'network', 'timeout'
    )

admin.site.register(SessionType, SessionTypeAdmin)


class SessionImageAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'name', 'tag', 'display_name'
    )

admin.site.register(SessionImage, SessionImageAdmin)


class SessionAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'created', 'account', 'user', 'image', 'command', 'worker',
        'status', 'active', 'ready', 'started', 'updated', 'stopped'
    )
    list_filter = ('worker', 'image', 'active')
    readonly_fields = ['started', 'updated', 'stopped']
    actions = ['start', 'update', 'monitor', 'stop']

    def start(self, request, queryset):
        for session in queryset:
            session.start()
        self.message_user(request, "%s sessions started." % len(queryset))
    start.short_description = 'Start session'

    def update(self, request, queryset):
        for session in queryset:
            session.update()
        self.message_user(request, "%s sessions updated." % len(queryset))
    update.short_description = 'Update session status'

    def monitor(self, request, queryset):
        for session in queryset:
            session.monitor()
        self.message_user(request, "Monitored %s sessions." % len(queryset))
    monitor.short_description = 'Monitor session'

    def stop(self, request, queryset):
        for session in queryset:
            session.stop(
                user='hub'
            )
        self.message_user(request, "%s sessions stopped." % len(queryset))
    stop.short_description = 'Stop session'

admin.site.register(Session, SessionAdmin)


class SessionStatsAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'session', 'time',
        'cpu_user', 'cpu_system',
        'mem_rss', 'mem_vms'
    )
    list_filter = ('session',)
    search_fields = ('session',)
    readonly_fields = ['session', 'data'] + list(SessionStats.stat_fields)

admin.site.register(SessionStats, SessionStatsAdmin)


class SessionLogsAdmin(admin.ModelAdmin):

    list_display = ('id', 'session', 'captured')
    list_filter = ('session', 'captured')
    search_fields = ('session', 'captured')
    readonly_fields = ('session', 'captured', 'logs')

admin.site.register(SessionLogs, SessionLogsAdmin)
