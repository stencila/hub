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

from invitations.models import Invitation


class InvitationAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'inviter', 'invitee', 'path', 'expiry',
        'sent', 'accepted', 'accepter'
    )
    readonly_fields = ('created', 'sent', 'accepted', 'accepter')
    list_filter = ('sent', 'accepted')
    actions = ('send',)

    def send(self, request, queryset):
        for invitation in queryset:
            invitation.send()
        self.message_user(request, "%s invitations sent." % len(queryset))
    send.short_description = 'Send invitation'

admin.site.register(Invitation, InvitationAdmin)
