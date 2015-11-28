from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from general.authentication import require_authenticated
from general.api import api, API
from components.models import Component, READ
from sessions_.models import Session_


@csrf_exempt  # Must come first!
@require_authenticated
@require_http_methods(["GET", "POST"])
def list_or_create(request):
    if(request.method == 'GET'):
        return list(request)
    else:
        return create(request)


def list(request):
    '''
    Get a list of sessions.

    Currently restricted to sessions for the current user. But account owners
    may want to get sessions for all users in account. Should be filterable.
    '''
    sessions = Session_.objects.filter(user=request.user)
    return api(request, sessions)


def create(request):
    '''
    Create a session for the component/user.

    Starts a new session, if there is not already an active
    one for the component/user pair, and returns it's details so that
    the client can connect to that session via websockets
    '''
    api = API(request)
    component = Component.one_if_authorized_or_raise(
        request.user,
        READ,
        address=api.required('address')
    )
    session = Session_.get_or_launch(
        component=component,
        user=request.user,
    )
    return api.respond(session)


@require_authenticated
@require_GET
def read(request, id):
    '''
    Read a session

    Checks that the user is authorized to read the session.
    '''
    session = Session_.objects.get(id=id)
    session.authorize_or_raise(request.user)
    session.update()
    return api(request, session)


@require_authenticated
@require_GET
def connect(request, id):
    '''
    Connect to a session

    Checks that the user is authorized to connect to the session.
    Get Nginx to proxy websocket connections to the session.
    For debugging purposes show the redirect header in the response content.
    '''
    session = Session_.objects.get(id=id)
    session.authorize_or_raise(request.user)

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
        return api({
            'message': 'Not ready, please try again later.'
        })


@csrf_exempt  # Must come first!
@require_authenticated
@require_POST
def stop(request, id):
    '''
    Stop a session

    Checks that the user is authorized to stop the session.
    '''
    session = Session_.objects.get(id=id)
    session.authorize_or_raise(request.user)
    session.stop()
    return api(request, session)
