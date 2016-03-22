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

from users.models import UserDetails, UserToken, UserEvent


class UserDetailsAdmin(admin.ModelAdmin):

    list_display = ('id', 'get_username', 'guest', 'builder', 'tester', 'get_last_login')

    def get_username(self, obj):
        return obj.user.username
    get_username.admin_order_field = 'user__username'
    get_username.short_description = 'Username'

    def get_last_login(self, obj):
        return obj.user.last_login
    get_last_login.admin_order_field = 'user__last_login'
    get_last_login.short_description = 'Last login'

admin.site.register(UserDetails, UserDetailsAdmin)


class UserTokenAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'issued', 'expires')

admin.site.register(UserToken, UserTokenAdmin)


class UserEventAdmin(admin.ModelAdmin):

    list_display = ('id', 'datetime', 'user', 'name')

admin.site.register(UserEvent, UserEventAdmin)
