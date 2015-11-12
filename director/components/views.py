import os
import mimetypes
# Add missing MIME type extensions
mimetypes.add_type('application/font-woff', '.woff')
from urlparse import urlparse

import django
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import (
    require_http_methods, require_GET, require_POST,
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import (
    csrf_exempt
)
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden

from general.authentication import unauthenticated_response, require_authenticated
from general.api import API
from visits.models import Visit
from components.models import Component, Address, Key, READ, ANNOTATE, UPDATE, DELETE, CREATE


######################################################################################
# Component

@csrf_exempt
def component_list(request):
    '''
    For:
        GET /components
        POST /components
    '''
    api = API(request)
    if api.get:
        components = Component.list(
            user=request.user,
            address=api.optional('address'),
            shown=api.optional('shown', True, lambda value: bool(int(value))),
            sort=api.optional('sort', 'id')
        )
        return api.respond(
            data=components,
            paginate=25
        )
    elif api.post:
        api.authenticated_or_raise()
        component = Component.create_one(
            user=request.user,
            address=api.required('address'),
            type=api.required('type'),
        )
        return api.respond(
            data=component
        )
    else:
        api.raise_method_not_allowed()


@csrf_exempt
def component_one(request, id):
    '''
    For:
        GET /components/{id}
        PATCH /components/{id}
        DELETE /components/{id}
    '''
    api = API(request)
    if api.get:
        component = Component.read_one(
            id=id,
            user=request.user,
        )
        return api.respond(
            data=component
        )
    elif api.patch:
        # Currently, PATCH is not valid for components
        api.raise_method_not_allowed()
        # api.authenticated_or_raise()
        # component = Component.update_one(
        #    id=id,
        #    user=request.user,
        #    data=api.data
        # )
        # return api.respond(
        #    data=component
        # )
    elif api.delete:
        api.authenticated_or_raise()
        Component.delete_one(
            id=id,
            user=request.user
        )
        return api.respond()
    else:
        api.raise_method_not_allowed()


@csrf_exempt
def component_star(request, id):
    '''
    Add/remove the component to/from the request user's starred list
    For:
        PUT /components/{id}/star
        DELETE /components/{id}/star
    '''
    api = API(request)
    api.authenticated_or_raise()
    component = Component.get(
        id=id,
        user=request.user,
        action=READ
    )
    if api.put:
        component.star(request.user)
    elif api.delete:
        component.unstar(request.user)
    else:
        api.raise_method_not_allowed()
    return api.respond({
        'stars': component.stars,
        'starred': component.starred(request.user)
    })


@csrf_exempt
def component_fork(request, id):
    '''
    Fork a component
    For:
        POST /components/{id}/fork
    '''
    api = API(request)
    api.authenticated_or_raise()
    component = Component.get(
        id=id,
        user=request.user,
        action=READ,
    )
    if api.post:
        fork = component.fork(
            user=request.user,
            to=api.required('to')
        )
        return api.respond(fork)
    else:
        api.raise_method_not_allowed()


def component_forks(request, id):
    '''
    Get a list of a component's forks
    For:
        GET /components/{id}/forks
    '''
    api = API(request)
    component = Component.one_if_authorized_or_raise(
        user=request.user,
        action=READ,
        id=id
    )
    if api.get:
        forks = component.forks(user)
        return api.respond(forks)
    else:
        api.raise_method_not_allowed()


@require_authenticated
@require_GET
def content(request, address):
    '''
    Get the current content of a component
    '''
    component = Component.one_if_authorized_or_raise(request.user, READ, address=address)
    api = API(request)
    format = request.GET.get('format')
    result = component.content(
        request.user,
        format,
    )
    return api.respond(result)

@csrf_exempt  # Must come first!
@require_authenticated
@require_POST
def save(request, address):
    '''
    Save the content of a component
    '''
    component = Component.one_if_authorized_or_raise(request.user, UPDATE, address=address)
    api = API(request)
    result = component.save_do(
        request.user,
        api.required('format'),
        api.required('content'),
        api.required('revision'),
    )
    return api.respond(result)


@require_GET
def component_extras(request, address):
    '''
    Provide extra content for a component page.

    This view is called asynchronusly by stencila.js and loads HTML/Javascript to the
    component page (e.g whitelabelled header and footer for a company account).
    Alternatives to this client side injection are:

        - server side injection - then the HTML changes each time, it can't be cached or 304ed
        - using an <iframe> wrapper - not clear what consequences are for SEO; need a separate request for the iframe's src?
    '''
    # URL requesting the extras
    url = request.GET.get('url')
    if url:
        url = urlparse(url)
        path = url.path
    else:
        path = ''
    return render(request, 'components/extras.html', {
        'address': address,
        'path': path,
    })


@csrf_exempt  # Must come first!
@require_POST
def received(request):
    '''
    Endpoint for the `curator` to ping when a component has
    received an update e.g. from `git push`. A token is used to protect access.
    But this endpoint only accepts the address of the component and then fetches an
    update from the `curator`, so a malicious user can not read or write data anyway.
    '''
    api = API(request)
    # Check access token
    try:
        token = api.required('token')
    except RuntimeError:
        return HttpResponseForbidden()
    if token != settings.COMMS_TOKEN:
        return HttpResponseForbidden()
    # Update the component
    component = Component.one_or_raise(address=api.required('address'))
    component.update()
    return api.respond()

# Component HTML and Redirecting views


@login_required
def new(request, type):
    '''
    Create a new component for the user and redirect them
    to it's canonical page
    '''
    if request.user_agent.is_bot:
        return redirect('/', permanent=True)
    else:
        component = Component.create(request.user, address=None, type=type)
        return redirect(component.url)


def page(request, address, component=None):
    '''
    Serve a component page.
    Not a view, but used by views below
    '''
    if component and not request.user_agent.is_bot:
        # Record the visit
        Visit.record(request, address, 'view')
        # Increment view count for this component
        component.views += 1
        component.save()
    # Return the `page.html` of the component
    if settings.MODE == 'local':
        # In `local` mode serve the static file
        return django.views.static.serve(request, '%s/index.html' % address, document_root='/srv/stencila/store')
    else:
        # Otherwise, ask Nginx to serve it
        # For debugging purposes show the redirect header in the response content
        url = '/internal-component-raw/%s/index.html' % address
        response = HttpResponse('X-Accel-Redirect : %s' % url)
        response['X-Accel-Redirect'] = url
        return response


@require_GET
def route(request, address=''):
    '''
    Route a request for component/s at an address

    If the address matches that of a single component then
    open in. Otherwise show a list of all components which have
    the address as a prefix
    '''
    # Remove any trailing slash for address matches
    if address.endswith('/'):
        address = address[:-1]
    # Check to see if there is a component matching this address
    # which the user is authorized to read
    component = Component.get(
        id=None,
        user=request.user,
        action=READ,
        address=address
    )
    if component:
        # Yes, return the components page or
        # redirect to the component's canonical URL if necessary
        if request.path == component.url():
            return page(request, address, component)
        else:
            return redirect(component.url(), permanent=True)
    else:
        # Is there an `all` stencil at the address?
        all = address+'/all'
        component = Component.get(request.user, READ, address=all)
        if component:
            # Yes, return that all stencil's page; ensure trailing slash
            if request.path.endswith('/'):
                return page(request, all, component)
            else:
                return redirect(request.path+'/')
        else:
            # Is there an `any` stencil at the parent address?
            parts = address.split('/')
            any = '/'.join(parts[:-1]) + '/any'
            component = Component.get(request.user, READ, address=any)
            if component:
                # Yes, return that any stencil's page; ensure trailing slash
                if request.path.endswith('/'):
                    return page(request, any, component)
                else:
                    return redirect(request.path+'/')
            else:
                # No, respond with stencil that provides a listing of
                # components at the address
                return page(request, '/core/stencils/index')


@require_GET
def slugified(request, address, slug):
    '''
    View a component's page with a slugified URL. Checks the slug is correct.
    '''
    component = Component.one_if_authorized_or_raise(request.user, READ, address=address)
    # If the slug is correct return the page
    if slug == component.slug:
        return page(request, address, component)
    # otherwise redirect to canonical URL with the correct slug
    else:
        return redirect(component.url, permanent=True)


@require_GET
def tiny(request, tiny):
    '''
    Redirect a tiny URL to the component's canonical URL
    '''
    id = Component.tiny_convert(tiny)
    component = Component.one_if_authorized_or_raise(request.user, READ, id=id)
    return redirect(component.url, permanent=True)


@csrf_exempt  # Required because git does not send CSRF tokens. Must be first decorator!
@require_http_methods(['GET', 'POST'])
def git(request, address):
    '''
    Serve a component repository.

    This view is used by Git clients to clone/pull/push to/from component respositories
      e.g. using the git shell program: git clone https://stenci.la/some/component
      e.g. using libgit2 integrated into stencila: stencil.pull()
    These commands results in requests to .git subdirectory of the component directory.

    Authentication will normally be done by UserToken via BasicAuth which uses the "Authorization"
    HTTP header. You can specify token (and no password) like this:

        git clone http://01sVr0jlc03M4qIBC1MQazbOlZvtcZZT5DkQ3Ir8uhMaEcoZhMo8dhHwvrFlKuVjRO:none@localhost:8010/235.git

    Note that Git does not supply the "Authorization" header until challenged to authenticate
    with a 401 header. So, a 401 response at first will be a normal part of the communications with Git
    for requests requiring UPDATE rights. If auth is not provided in the URL as above then
    the Git client will prompt for username/password.

    This method has to be csrf_exempt otherwise Git can not POST to it because it
    does not have a Django CRSF token.

    This view authorization and then gets `git-http-backend.go` to handle
    the request via an Nginx X-Accel-Redirect. `git-http-backend.go` is a Go implementation of
    the (C CGI backend)[http://git-scm.com/docs/git-http-backend].
    It is (should be?) faster and (for me) required less configuration to get working
    than the C CGI backend.
    '''
    # Get component
    component = Component.one_or_raise(address=address)
    # Authorize action
    service = request.GET.get('service')
    if request.method == 'GET':
        # A push involves a GET of git-receive-pack first.
        # So require UPDATE for this request
        if service == 'git-receive-pack':
            action = UPDATE
        else:
            action = READ
    else:
        # A pull, clone etc involves a POST to /foo/.git/git-upload-pack
        # So only require READ for this request
        if 'git-upload-pack' in request.path:
            action = READ
        else:
            action = UPDATE
    # If action requires UPDATE then the user must be authenticated first
    if action == UPDATE and not request.user.is_authenticated():
        return unauthenticated_response()
    else:
        component.authorize_or_raise(request.user, action)
    # Respond
    # Ask Nginx to do a proxy pass.
    # Replace '<address>.git' with '<address>/.git'
    url = '/internal-component-git' + request.get_full_path().replace('.git', '/.git')
    # For debugging purposes show the redirect header in the response content
    response = django.http.HttpResponse('Internal redirect to : %s' % url)
    response['X-Accel-Redirect'] = url
    return response


@require_GET
def raw(request, path):
    '''
    Serve a raw component file

    Does authorization and then gets Nginx to serve the file using X-Accel-Redirect
    '''
    # Get component and authorise READ
    component = None
    address = os.path.dirname(path)
    while len(address) > 0:
        try:
            component = Component.objects.get(address=address)
        except ObjectDoesNotExist:
            address = os.path.dirname(address)
        else:
            break
    if component is None:
            raise Http404()
    component.authorize_or_raise(request.user, READ)
    # Check it exists
    full_path = os.path.join('/srv/stencila/store', path)
    if not os.path.exists(full_path):
        raise Http404()
    # Respond
    response = django.http.HttpResponse()
    if django.conf.settings.MODE == 'local':
        return django.views.static.serve(request, path, document_root='/srv/stencila/store')
    else:
        # Tell Nginx what to serve
        response['X-Accel-Redirect'] = '/internal-component-raw/%s' % path
        # Delete the default text/html content type so Nginx decides what it should be
        response.__delitem__('Content-Type')
    return response


######################################################################################
# Address

@csrf_exempt
def address_list(request):
    '''
    For:
        GET /addresses
        POST /addresses
    '''
    api = API(request)
    api.authenticated_or_raise()
    if api.get:
        addresses = Address.list(
            user=request.user
        )
        return api.respond(
            data=addresses,
            paginate=100
        )
    elif api.post:
        address = Address.create_one(
            user=request.user,
            address=api.required('address'),
            type=api.required('type'),
            action=api.required('action'),
            users=api.required('users')
        )
        return api.respond(
            data=address
        )
    else:
        return api.raise_method_not_allowed()


@csrf_exempt
def address_one(request, id):
    '''
    For:
        GET /addresses/{id}
        PATCH /addresses/{id}
        DELETE /addresses/{id}
    '''
    api = API(request)
    api.authenticated_or_raise()
    if api.get:
        address = Address.read_one(
            id=id,
            user=request.user
        )
        return api.respond(
            data=address
        )
    elif api.patch:
        address = Address.update_one(
            id=id,
            user=request.user,
            data=api.data
        )
        return api.respond(
            data=address
        )
    elif api.delete:
        address = Address.delete_one(
            id=id,
            user=request.user
        )
        return api.respond()
    else:
        api.raise_method_not_allowed()


######################################################################################
# Key

@csrf_exempt
def key_list(request):
    '''
    For:
        GET /keys
        POST /keys
    '''
    api = API(request)
    api.authenticated_or_raise()
    if api.get:
        keys = Key.list_user(
            user=request.user
        )
        return api.respond(
            data=keys,
            paginate=True
        )
    elif api.post:
        key = Key.create_one(
            user=request.user,
            address=api.required('address'),
            type=api.required('type'),
            action=api.required('action'),
            users=api.required('users')
        )
        return api.respond(
            data=key
        )
    else:
        return api.raise_method_not_allowed()


@csrf_exempt
def key_one(request, id):
    '''
    For:
        GET /keys/{id}
        PATCH /keys/{id}
        DELETE /keys/{id}
    '''
    api = API(request)
    api.authenticated_or_raise()
    if api.get:
        key = Key.read_one(
            id=id,
            user=request.user
        )
        return api.respond(
            data=key
        )
    elif api.patch:
        key = Key.update_one(
            id=id,
            user=request.user,
            data=api.data
        )
        return api.respond(
            data=key
        )
    elif api.delete:
        key = Key.delete_one(
            id=id,
            user=request.user
        )
        return api.respond()
    else:
        api.raise_method_not_allowed()
