from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from general.authentication import require_authenticated
from general.api import API
from components.models import Component, READ
from sessions_.models import Session, SessionType, SessionImage
from users.views import testing


@csrf_exempt
def sessions(request, id=None):
    api = API(request)
    if id is None:
        if api.get:
            # Get a list of sessions
            sessions = Session.list(
                user=request.user,
                filter={
                    'active': True
                }
            )
            return api.respond(
                sessions,
                template='sessions/list.html',
                context={
                    'sessions': sessions,
                    'types': SessionType.objects.order_by('rank').all(),
                    'images': SessionImage.objects.all()
                }
            )
        elif api.post:
            # Launch a session for the user
            session = Session.launch(
                user=request.user,
                type_id=api.required('type'),
                image_name=api.require('image')
            )
            return api.respond(session)
    else:
        if api.get:
            # Get a session, updating it first
            session = Session.get(
                id=id,
                user=request.user
            )
            if session.active:
                session.update()
            return api.respond(session)

    return api.respond(status=405)


@login_required
def new(request):
    '''
    List session types, create a new session, launch it and redirect the
    user to it's page
    '''
    api = API(request)
    if api.get:
        return api.respond(
            template='sessions/new.html',
            context={
                'sessions': Session.list(
                    user=request.user,
                    filter={
                        'active': True
                    }
                ),
                'types': SessionType.objects.all(),
                'images': SessionImage.objects.all()
            }
        )
    elif api.post:
        session = Session.launch(
            user=request.user,
            type_id=api.required('type'),
            image_name=api.required('image')
        )
        return api.respond_created(url=session.url())

    return api.respond_bad()


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
        url = '/internal-session-websocket/%s:%s' % (
            session.worker.ip,
            session.port
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

    Return `ready` value.
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
            return api.respond({
                'ready': session.ready
            })
        else:
            return api.respond({
                'error': 'session:inactive',
                'message': 'Session is no longer active'
            })
    else:
        raise API.MethodNotAllowedError(method=request.method)


@csrf_exempt
@require_authenticated
def stop(request, id):
    '''
    Stop a session
    '''
    api = API(request)
    if api.put:
        session = Session.get(
            id=id,
            user=request.user
        )
        session.stop(request.user)
        return api.respond(session)
    else:
        raise API.MethodNotAllowedError(method=request.method)
