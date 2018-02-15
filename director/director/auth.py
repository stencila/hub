from django.contrib.auth import authenticate, login

def login_guest_user(request):
    '''
    Creates a guest user
    '''
    user = authenticate(stencila_guest_auth=True)
    login(request, user)
