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


class AccountUrlRoot(enum.Enum):
    """
    These are the components used after the account root URL.

    They will either be used in the URL like /accounts/<id>/<value> or with a slug prefix /<account-slug>/value/

    A project slug can not be one of these.
    """

    create = 'create'
    members = 'members'
    settings = 'settings'
    teams = 'teams'
    subscriptions = 'subscriptions'
    subscription_signup = 'subscription-signup'


# A set of slugs that are not allowed to be used as they conflict with our URLs
DISALLOWED_ACCOUNT_SLUGS = {u.value for u in UrlRoot}.union({'static', 'media'})
DISALLOWED_PROJECT_SLUGS = {u.value for u in AccountUrlRoot}
