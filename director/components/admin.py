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

from reversion.admin import VersionAdmin

from components.models import Component, Address, Key, Snapshot


class ComponentAdmin(VersionAdmin):

    list_display = ('id', 'address', 'type', 'title', 'initialised', 'updated', 'published', 'views', 'stars', 'forks')
    list_filter = ('type', 'published')
    actions = ['init', 'update']

    def init(self, request, queryset):
        for com in queryset:
            com.initialise()
        self.message_user(request, "%s components initialised" % len(queryset))
    init.short_description = 'Initialise component repo'

    def update(self, request, queryset):
        for com in queryset:
            com.update()
        self.message_user(request, "%s components updated." % len(queryset))
    update.short_description = 'Update component'

admin.site.register(Component, ComponentAdmin)


class AddressAdmin(admin.ModelAdmin):

    list_display = ('id', 'public')
    list_filter = ('public',)

admin.site.register(Address, AddressAdmin)


class KeyAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'address', 'type', 'action', 'get_usernames')
    list_filter = ('type', 'action')

    def get_queryset(self, request):
        queryset = super(KeyAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related('users')
        return queryset

    def get_usernames(self, obj):
        return ','.join([user.username for user in obj.users.all()]) if obj.users else None
    get_usernames.short_description = 'Users'

admin.site.register(Key, KeyAdmin)


class SnapshotAdmin(admin.ModelAdmin):

    list_display = ('id', 'component', 'user', 'datetime')
    list_filter = ('user',)

admin.site.register(Snapshot, SnapshotAdmin)
