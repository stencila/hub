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

'''
Defines some common, "general" views not tied to a specific app.
'''
import json
from collections import OrderedDict

from django.template import Context, loader
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.http import Http404
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder

from components.models import Component
from general.api import API
from general.errors import Error

# Front pages


def front(request):
    '''
    Front page at / dispatches to about or explore depending upon
    if user is logged in
    '''
    return explore(request) if request.user.is_authenticated() else about(request)


def about(request):
    '''
    About Stencila
    '''
    return render(request, 'about.html')


def explore(request):
    '''
    Explore components
    '''
    components = Component.list(
        user=request.user,
        published=True,
        sort='-id'
    )
    return render(request, 'explore.html', {
        'components': components
    })


# API documentation

def api_ui(request):
    '''
    Render API documentation template based on Swagger UI but with
    header and footer etc
    '''
    return render(request, 'api.html')


def api_yml(request):
    '''
    Render API Swagger specification. This is templated
    to allow for the UI to be used in local development mode
    '''
    return render(request, 'api.yml')


# Custom error views
#  See https://docs.djangoproject.com/en/1.9/topics/http/views/#customizing-error-views
# At time of writing, 400, 403, 404 and 500 are the only codes which have custom handling

def render_error(request, template):
    template = loader.get_template(template)
    try:
        sentry_id = request.sentry['id']
    except:
        sentry_id = None
    data = dict(
        uri=request.build_absolute_uri(),
        remote=request.META.get('REMOTE_ADDR'),
        sentry_id=sentry_id
    )
    return template.render({
        'comment_end': '-->',
        'comment_begin': '<!--',
        'data': json.dumps(data, cls=DjangoJSONEncoder, indent=4),
        'sentry_id': sentry_id
    })


def handler400(request):
    '''
    Bad request handler
    '''
    return HttpResponseBadRequest(render_error(request, '4xx.html'))


def handler403(request):
    '''
    Permission denied handler
    '''
    return HttpResponseForbidden(render_error(request, '403.html'))


def handler404(request):
    '''
    Not found handler
    '''
    return HttpResponseNotFound(render_error(request, '404.html'))


def handler500(request):
    '''
    Server error handler.
    Includes `request` in the context so that a Sentry case reference id can be reported.
    '''
    return HttpResponseServerError(render_error(request, '5xx.html'))


# Test error views are used to test that the correct templates
# are being used for errors and that error reporting (currently via Sentry)(
# is behaving as intended.


@staff_member_required
def test400(request):
    raise SuspiciousOperation('You should see this in DEBUG mode but in production see a custom 400 page')


@staff_member_required
def test403(request):
    raise PermissionDenied()


@staff_member_required
def test404(request):
    raise Http404()


@staff_member_required
def test500(request):
    # Supposedly a SystemExist exception is ignored by the test client - but it wasn't for me
    # https://docs.djangoproject.com/en/1.7/topics/testing/tools/#exceptions
    # A plain old exception at least gets reportest in the debugger
    raise Exception('Faked server error')


@staff_member_required
def test_custom_error(request):
    raise Error()


def test_user_agent(request):
    '''
    For testing what django-user-agents and our internal request handler
    is returning for different, ummm, user agents
    '''
    rh = API(request)
    ua = request.user_agent
    return rh.respond(OrderedDict([
        ('rh_accept', rh.accept),
        ('rh_browser', rh.browser),
        ('ua_is_mobile', ua.is_mobile),
        ('ua_is_tablet', ua.is_tablet),
        ('ua_is_touch_capable', ua.is_touch_capable),
        ('ua_is_pc', ua.is_pc),
        ('ua_is_bot', ua.is_bot),
        ('ua_browser', ua.browser),
        ('ua_browser_family', ua.browser.family),
        ('ua_browser_version', ua.browser.version),
        ('ua_browser_version_string', ua.browser.version_string),
        ('ua_os', ua.os),
        ('ua_os_family', ua.os.family),
        ('ua_os_version', ua.os.version),
        ('ua_os_version_string', ua.os.version_string),
        ('ua_device', ua.device),
        ('ua_device_family', ua.device.family),
    ]))


def backend_error(request, backend, url):
    '''
    Used to capture and report backend requests to Sentry.
    Only intended to be called internally by Nginx.
    Note that when doing `usgwi_param` the name of the header
    is NOT converted to `HTTP_X_INTERNAL`.
    '''
    internal = request.META.get('X-Internal')
    if internal == 'yes':
        raise BackendError('%s : %s' % (backend, url))
    else:
        return HttpResponseForbidden('X-Internal: %s' % internal)


class BackendError(Exception):
    pass
