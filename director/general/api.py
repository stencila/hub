'''
A module for reducing boilerplate code and
providing consistency in API views
'''

import json

from django.db.models import Model, QuerySet
from django.http import JsonResponse
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger

from general.errors import Error


class API:
    '''
    An API request wrapper. Parses JSON body and
    provides some syntactic sugar. Instantiate an API instance
    within API related views.
    '''
    def __init__(self, request):
        self.request = request
        self.post = (request.method == 'POST')
        self.get = (request.method == 'GET')
        self.put = (request.method == 'PUT')
        self.patch = (request.method == 'PATCH')
        self.delete = (request.method == 'DELETE')

        self.data = {}
        if self.get:
            self.data = request.GET
        elif self.post or self.patch:
            try:
                self.data = json.loads(request.body)
            except ValueError:
                raise API.JsonInvalidError(json=request.body)

    def required(self, name, converter=lambda x: x):
        '''
        Get a required parameter from the request.
        '''
        try:
            return converter(self.data[name])
        except KeyError:
            raise API.ParameterRequiredError(parameter=name)

    def optional(self, name, default=None, converter=lambda x: x):
        '''
        Get an optional parameter from the request.
        '''
        return converter(self.data.get(name, default))

    def respond(self, data=None, paginate=0):
        '''
        Respond to the request with some data.
        '''
        if paginate:
            pages = Paginator(data, paginate)
            page_number = self.optional('page')
            try:
                # Get requested page
                page = pages.page(page_number)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                page = pages.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                page = pages.page(pages.num_pages)
            # Create a response
            data = [item.serialize(self.request.user) for item in page.object_list]
            response = JsonResponse(data, safe=False)
            # Add pagination headers
            link = ''
            # Get URL and remove page number parameter so it is not repeated
            url = '%s://%s%s' % (self.request.scheme, self.request.get_host(), self.request.path)
            parameters = self.request.GET.copy()
            try:
                parameters.pop('page')
            except KeyError:
                pass

            def create_link(page, rel):
                '''
                Create pagination link headers
                '''
                parameters['page'] = page
                return '<%s?%s>; rel="%s",' % (url, parameters.urlencode(), rel)

            if page.has_next():
                link += create_link(page.next_page_number(), 'next')
            if page.has_previous():
                link += create_link(page.previous_page_number(), 'prev')
            link += create_link(1, 'first')
            link += create_link(pages.num_pages, 'last')
            response['Link'] = link

            return response
        else:
            if(data is None):
                data = {}
            elif isinstance(data, Model):
                data = data.serialize(self.request.user)
            elif isinstance(data, QuerySet):
                data = [item.serialize(self.request.user) for item in data]
            return JsonResponse(data, safe=False)

    def authenticated_or_raise(self):
        if not self.request.user.is_authenticated():
            raise API.UnauthenticatedError(self.request.path, self.request.method)

    def raise_method_not_allowed(self):
        raise API.MethodNotAllowedError(self.request.method)

    def raise_not_found(self):
        raise API.NotFoundError()

    class UnauthenticatedError(Error):
        code = 401

        def __init__(self, endpoint, method):
            self.endpoint = endpoint
            self.method = method

        def serialize(self):
            return dict(
                error="unauthenticated",
                message='Authentication is required for this endpoint/method',
                url='https://stenci.la/api/errors/unauthenticated',
                endpoint=self.endpoint,
                method=self.method
            )

    class MethodNotAllowedError(Error):
        code = 405

        def __init__(self, method):
            self.method = method

        def serialize(self):
            return dict(
                error="method-not-allowed",
                message='Method is not allowed for this endpoint',
                url='https://stenci.la/api/errors/method-not-allowed',
                method=self.method
            )

    class JsonInvalidError(Error):
        code = 400

        def __init__(self, json):
            self.json = json

        def serialize(self):
            return dict(
                error="json-invalid",
                message='The supplied JSON could not be parsed',
                url='https://stenci.la/api/errors/json-invalid',
                json=self.json
            )

    class ParameterRequiredError(Error):
        code = 400

        def __init__(self, parameter):
            self.parameter = parameter

        def serialize(self):
            return dict(
                error="parameter-required",
                message='Required parameter was not supplied',
                url='https://stenci.la/api/errors/parameter-required',
                parameter=self.parameter
            )

    class NotFoundError(Error):
        code = 404

        def __init__(self):
            pass

        def serialize(self):
            return dict(
                error="not-found",
                message='Resource not found'
            )
