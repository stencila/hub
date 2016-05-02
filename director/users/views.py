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

from django.views.decorators.http import require_http_methods, require_GET
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.shortcuts import redirect

import allauth.account.views

from users.models import User, UserToken, UserEvent
from general.api import API
from general.authentication import require_authenticated

# Decorators to be used in other apps

def testing(function):
    '''
    A view decorator to only allow testers
    '''
    def wrap(request, *args, **kwargs):
        if request.user.details.tester:
            return function(request, *args, **kwargs)
        else:
            api = API(request)
            return api.respond(
                data={
                    'error': 'user:not-tester',
                    'message': 'This page or API endpoint is only available to testers. See https://stenci.la/users/testers',
                },
                template='users/testers.html',
                status=403
            )

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

# Overrides of allauth urls and templates


class SignupView(allauth.account.views.SignupView):

    template_name = "users/signup.html"

signup = SignupView.as_view()


class SigninView(allauth.account.views.LoginView):

    template_name = "users/signin.html"

signin = SigninView.as_view()


class SigninDialogView(allauth.account.views.LoginView):

    template_name = "users/signin_dialog.html"

signin_dialog = SigninDialogView.as_view()


class SignoutView(allauth.account.views.LogoutView):

    template_name = "users/signout.html"

signout = SignoutView.as_view()


def join(request):
    '''
    Allow a guest to become a full user:
        - upgrade account
        - turn user.deails.guest = False 
    '''
    # TODO Right now just sign them out and redirect to
    # signup page
    if request.user.is_authenticated() and request.user.details.guest:
        logout(request)
        return redirect('/me/signup')
    else:
        return redirect('/')


@require_GET
def me_read(request):
    '''
    Read the currently authenticated user
    '''
    # Call `serialize()` instead of just passing `request.user`
    # to `api` which does not handle `SimpleLazyObject`
    return API(request).respond(
        request.user.serialize(request)
    )


@require_GET
def users_list(request):
    '''
    List users
    '''
    return API(request).respond(
        User.objects.all(),
        paginate=100
    )


@require_GET
def users_read(request, username):
    '''
    Read a user
    '''
    api = API(request)
    try:
        return api.respond(User.objects.get(username=username))
    except User.DoesNotExist:
        raise Http404


@require_GET
def settings(request):
    return API(request).respond(
        request.user.serialize(request),
        template='users/settings.html'
    )


@csrf_exempt
@require_authenticated
@require_http_methods(["GET", "POST", "PATCH", "DELETE"])
def tokens(request, id=None):
    '''
    List, create, read, update, delete user tokens
    '''
    api = API(request)
    if id is None:
        if api.get:
            # List all tokens for the user
            tokens = UserToken.objects.filter(
                user=request.user
            )
            return api.respond(tokens)
        elif api.post:
            # Create a token for the user
            token = UserToken.objects.create(
                user=request.user,
                name=api.optional('name'),
                notes=api.optional('notes')
            )
            return api.respond(token)
    else:
        # Get token, ensuring it is associated with the
        # request user
        token = UserToken.get_or_raise(
            id=id,
            user=request.user
        )
        if api.get:
            # Read it
            return api.respond(token)
        elif api.patch:
            # Update it
            token.name = api.optional('name')
            token.notes = api.optional('notes')
            token.save()
            return api.respond(token)
        elif api.delete:
            # Delete it
            token.delete()
            return api.respond()

@csrf_exempt
def events(request):
    api = API(request)
    if api.post:
        UserEvent.create(
            user=request.user,
            name=api.required('name'),
            data=api.required('data')
        )
        return api.respond()
    else:
        return api.respond(status=405)
