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
from snippets.models import Snippet
from users.views import testing

@csrf_exempt
@testing
def snippets(request, id=None):
    api = API(request)
    if id is None:
        if api.get:
            snippets = Snippet.list()
            return api.respond(
            	snippets,
            	detail=0,
            	template='snippets/list.html',
            	context={
            		'languages':['js','jl','py','r']
            	}
            )
    else:
        if api.get:
            snippet = Snippet.get(
                id=id
            )
            return api.respond(
            	snippet,
            	template='snippets/get.html'
            )
        elif api.put:
            snippet = Snippet.put(
                user=request.user,
                id=id,
                spec=api.data
            )
            return api.respond(
            	snippet,
            	detail=0
            )

    raise API.MethodNotAllowedError(
        method=request.method
    )
