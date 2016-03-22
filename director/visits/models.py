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

from __future__ import unicode_literals

from django.db import models
from ipware.ip import get_real_ip

from users.models import User


class Visit(models.Model):

    when = models.DateTimeField(
        auto_now_add=True,
        null=True,
        help_text='Date/time of visit'
    )

    address = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text='Address of the component recording this visit'
    )

    view = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text='View recording this visit'
    )

    scheme = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        help_text='Scheme of the request (http or https usually)'
    )

    path = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text='Path to the requested page, not including the domain'
    )

    method = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        help_text='HTTP method used in the request'
    )

    type = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        help_text='User agent type'
    )

    touchable = models.NullBooleanField(
        null=True,
        blank=True,
        help_text='Is the user agent touch capable?'
    )

    device = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text='Device family'
    )

    browser = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text='Browser family'
    )

    browser_version = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text='Browser version'
    )

    referer = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text='The referring page, if any'
    )

    ip = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text='The IP address of the client'
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        help_text='The authenticated user, if any'
    )

    @staticmethod
    def record(request, address=None, view=None):
        visit = Visit()

        visit.address = address
        visit.view = view

        visit.scheme = request.scheme
        visit.path = request.path
        visit.method = request.method

        visit.type = None
        if request.user_agent.is_bot:
            visit.type = 'BOT'
        elif request.user_agent.is_mobile:
            visit.type = 'MOB'
        elif request.user_agent.is_tablet:
            visit.type = 'TAB'
        elif request.user_agent.is_pc:
            visit.type = 'COM'

        visit.touchable = request.user_agent.is_touch_capable

        visit.device = request.user_agent.device.family

        visit.browser = request.user_agent.browser.family
        visit.browser_version = request.user_agent.browser.version_string

        # Use get() because the HTTP_REFERER header is only there if this
        # visit was from a link on another page, not from a
        # type-the-url-into-the-browser visit
        visit.referer = request.META.get('HTTP_REFERER')

        visit.ip = get_real_ip(request)

        if request.user.is_authenticated():
            visit.user = request.user

        visit.save()
