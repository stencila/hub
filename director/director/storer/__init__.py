class Storer(object):
    code = None
    name = '?'

    def __init__(self, account=None):
        self.url = None
        self.account = account

    def __unicode__(self):
        return "Storer {}".format(self.name)

    def username(self):
        pass

    def profile_url(self):
        pass

    @classmethod
    def get_instance_by_provider(cls, provider, **kwargs):
        for subclass in cls.__subclasses__():
            if provider == subclass.code:
                return subclass(**kwargs)
        raise RuntimeError("Storer for {} not found".format(provider))

    @classmethod
    def get_instance_by_account(cls, account):
        return cls.get_instance_by_provider(account.provider, account=account)

from .github import GithubStorer
from .dropbox import DropboxStorer
from .google import GoogleStorer
from .stencila import StencilaStorer
