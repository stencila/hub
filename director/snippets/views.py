from django.views.decorators.csrf import csrf_exempt

from general.api import API
from snippets.models import Snippet


@csrf_exempt
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
            	snippet
            )
        elif api.put:
            snippet = Snippet.put(
                user=request.user,
                spec=request.body
            )
            return api.respond(
            	snippet
            )

    raise API.MethodNotAllowedError(
        method=request.method
    )
