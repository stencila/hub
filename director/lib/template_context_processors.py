from django.conf import settings


def sentry_js_url(request):
    return {'SENTRY_JS_URL': settings.SENTRY_JS_URL}
