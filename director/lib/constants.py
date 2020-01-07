import enum


class UrlRoot(enum.Enum):
    """
    Contains all the root URLs that we use in the base urlpatterns.

    The purpose of this is to make it easier to keep the list of disallowed account slugs up to date.
    """
    
    about = 'about'
    accounts = 'accounts'
    admin = 'admin'
    api = 'api'
    beta = 'beta'
    checkout = 'checkout'
    checkouts = 'checkouts'
    debug = 'debug'
    favicon = 'favicon.ico'
    ie_unsupported = 'ie-unsupported'
    me = 'me'
    open = 'open'
    projects = 'projects'
    stencila_admin = 'stencila-admin'
    system_status = 'system-status'
    test = 'test'


# A set of slugs that are not allowed to be used as they conflict with our URLs
DISALLOWED_ACCOUNT_SLUGS = {u.value for u in UrlRoot}.union({'static'})
