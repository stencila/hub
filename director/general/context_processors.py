from django.conf import settings


def custom(request):
    '''
    Adds some custom variables to template contexts
    '''
    return {
        'MODE': settings.MODE,
        'INTERCOM_ON': settings.INTERCOM_ON,
        'path': request.path,
    }
