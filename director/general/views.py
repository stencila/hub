'''
Defines some common, "general" views not tied to a specific app.
'''

from django.template import Context, loader
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.http import Http404
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from components.models import Component

def front(request):
    '''
    Front page at /
    '''
    components = Component.list(
        user=request.user,
        sort='-id'
    )
    return render(request, 'front.html', {
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

def handler400(request):
    '''
    Bad request handler
    '''
    template = loader.get_template('4xx.html')
    return HttpResponseBadRequest(template.render(Context({
        'request': request,
    })))


def handler403(request):
    '''
    Permission denied handler
    '''
    template = loader.get_template('403.html')
    return HttpResponseForbidden(template.render(Context({
        'request': request,
    })))


def handler404(request):
    '''
    Not found handler
    '''
    template = loader.get_template('404.html')
    return HttpResponseNotFound(template.render(Context({
        'request': request,
    })))


def handler500(request):
    '''
    Server error handler.
    Includes `request` in the context so that a Sentry case reference id can be reported.
    '''
    template = loader.get_template('5xx.html')
    return HttpResponseServerError(template.render(Context({
        'request': request,
        'comment_end': '-->',
        'comment_begin': '<!--'
    })))


# Test views are used to test that the correct templates
# are being used for errors and that error reporting (currently via Sentry)(
# is behaving as intended


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
    # Supposdly a SystemExist exception is ignored by the test client - but it wasn't for me
    # https://docs.djangoproject.com/en/1.7/topics/testing/tools/#exceptions
    # A plain old exception at least gets reportest in the debugger
    raise Exception('Faked server error')
