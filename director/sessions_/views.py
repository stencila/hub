from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from general.authentication import require_authenticated
from general.api import API
from components.models import Component, READ
from sessions_.models import Session


@csrf_exempt
@require_authenticated
def sessions(request, id=None):
    api = API(request)
    if id is None:
        if api.get:
            # Get a list of sessions
            sessions = Session.objects.filter(user=request.user)
            return api.respond(sessions)
        elif api.post:
            # Create a session for the component/user.
            # Starts a new session, if there is not already an active
            # one for the component/user pair, and returns it's details so that
            # the client can connect to that session via websockets
            component = Component.one_if_authorized_or_raise(
                request.user,
                READ,
                address=api.required('address')
            )
            session = Session.get_or_launch(
                component=component,
                user=request.user,
            )
            return api.respond(session)
    else:
        if api.get:
            session = Session.get(
                id=id,
                user=request.user
            )
            if session.active:
                session.update()
            return api.respond(session)

    raise API.MethodNotAllowedError(method=request.method)


@require_authenticated
@require_GET
def connect(request, id):
    '''
    Connect to a session

    Checks that the user is authorized to connect to the session.
    Get Nginx to proxy websocket connections to the session.
    For debugging purposes show the redirect header in the response content.
    '''
    session = Session.get(
        id=id,
        user=request.user
    )
    # If no port (i.e only just started) then update
    if not session.port:
        # Currently updating the task first but we could
        # fire off an aysnchonous celery task elsewhere so
        # client does not need to wait for this the first time
        session.update()
    # Try again
    if session.port:
        url = '/internal-session-websocket/%s:%s/%s' % (
            session.worker.ip,
            session.port,
            session.component.address.id
        )
        response = HttpResponse('X-Accel-Redirect : %s' % url)
        response['X-Accel-Redirect'] = url
        return response
    else:
        return API(request).respond({
            'message': 'Not ready, please try again later.'
        })

@csrf_exempt
@require_authenticated
def ping(request, id):
    '''
    Ping a session to keep it open

    Sessions that have not been pinged for sometime will be automatically
    stopped.
    '''
    api = API(request)
    if api.put:
        session = Session.get(
            id=id,
            user=request.user
        )
        if session.active:
            session.ping()
            return api.respond()
        else:
            return api.respond({
                'message': 'Session is no longer active'
            })
    else:
        raise API.MethodNotAllowedError(method=request.method)

@csrf_exempt  # Must come first!
@require_authenticated
@require_POST
def stop(request, id):
    '''
    Stop a session

    Checks that the user is authorized to stop the session.
    '''
    session = Session.get(id=id)
    session.stop()
    return API(request).respond(session)
