from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt

import allauth.account.views

from users.models import User, UserToken, UserEvent
from general.api import API
from general.authentication import require_authenticated

# Decorators to be used in other apps

def testers(function):
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


class SignoutView(allauth.account.views.LogoutView):

    template_name = "users/signout.html"

signout = SignoutView.as_view()


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
        api.raise_not_found()


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
