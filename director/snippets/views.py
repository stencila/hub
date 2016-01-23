from django.views.decorators.csrf import csrf_exempt

from general.api import API
from snippets.models import Snippet
from users.views import testers

@csrf_exempt
@testers
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
