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

from django.views.decorators.csrf import csrf_exempt

from general.api import API
from builds.models import Build


@csrf_exempt
def builds(request, id=None):
    api = API(request)
    if id is None:
        if api.get:
            builds = Build.list()
            return api.respond(
                builds,
                template='builds/builds.html'
            )
        elif api.post:
            build = Build.create(
                user=request.user,
                package=api.required('package'),
                flavour=api.required('flavour'),
                version=api.required('version'),
                commit=api.required('commit'),
                platform=api.optional('platform'),
                url=api.optional('url')
            )
            return api.respond(build)
    else:
        if api.get:
            build = Build.objects.get(
                id=id
            )
            return api.respond(build)

    raise API.MethodNotAllowedError(
        method=request.method
    )
