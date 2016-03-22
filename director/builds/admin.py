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

from builds.models import Build


class BuildAdmin(admin.ModelAdmin):

    list_display = ('id', 'package', 'flavour', 'version', 'commit', 'platform', 'get_username', 'datetime')

    def get_username(self, obj):
        return obj.user.username if obj.user else None
    get_username.admin_order_field = 'user__username'
    get_username.short_description = 'Username'

admin.site.register(Build, BuildAdmin)
