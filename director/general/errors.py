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
Base `Error` exception class and  `ErrorMiddleware`
for raising and handling error exceptions
'''
from django.http import JsonResponse


class Error(Exception):
    '''
    Base exception class for custom exceptions.
    Override the `serialize()` method
    '''

    code = 500

    def serialize(self):
        return dict(
            error='general-error',
            message='An error occurred'
        )


class ErrorMiddleware(object):
    '''
    Converts an `Error` exception into a HTML or JSON depending
    on the request type
    '''

    def process_exception(self, request, exception):
        if isinstance(exception, Error):
            return JsonResponse(
                exception.serialize(),
                status=exception.code
            )
