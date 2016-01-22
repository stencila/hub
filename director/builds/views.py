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
